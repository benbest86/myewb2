#!/usr/bin/perl

# What's our path?  Set it here so we can change it easily!
$path = "/home/myewb2/myewb/cron";

use Mail::Bulkmail  "/home/myewb2/myewb/cron/Mail/sample.cfg.file"; 
use MIME::Lite;
use Mysql;
use Text::Unaccent;

# Ensure only one instance of this script is running at a time by checking
#  for existance of temp file
if(!(-e "$path/running.txt"))
{
	#############################
	### SCRIPT INITIALIZATION ###
	#############################

	# Prepare to run by taking timestamp
	open(RESULTS, "> $path/notrunning.txt");
	$thestring = localtime;
	print RESULTS $thestring . "\n";
	close RESULTS;


	# Create temp file, indicating script is running		
	rename "$path/notrunning.txt", "$path/running.txt";

	# create a db connection
	$dbh = Mysql->connect('localhost', 'myewb', 'myewb2', '');
	
	$dbh->query("SET AUTOCOMMIT = 1");

	# get emails that need sending
	$result = $dbh->query("SELECT id, recipients, shortname,
		sender, subject, textMessage, htmlMessage, lang, cc, bcc
		FROM mailer_email WHERE progress='waiting'");
#	$result = $dbh->query('SELECT id, recipients, shortname,
#		sender, subject, textMessage, htmlMessage
#		FROM mailer_email WHERE recipients=\'feedback@my.ewb.ca\'');

	# Process each email individually
	while(@emails = $result->fetchrow) 
	{
		#######################
		### PARSE VARIABLES ###
		#######################

		# Parse fields into user-friendly variables!
		$id = $emails[0];
		# $emails[1] is the recipient list and will be parsed later
		$totalshortname = $emails[2];
		$sender = $emails[3];
		$subject = $emails[4];
		$textMessage = $emails[5];
		$htmlMessage = $emails[6];
		$lang = $emails[7];
		$cc = $emails[8];
		$bcc = $emails[9];

		#print STDOUT "Processing email #$ id \n";
	
		# Attempt to fix the Article of the Week triple-send thing...
		# by marking this as "in progress".		
		$dbh->query("UPDATE mailer_email SET progress='sending' WHERE id=$id");

		# Retrieve email addresses and sort into list
		@recipients = split(',', $emails[1]);

		# send to sender & admin
		$senderemail = $sender;
		$senderemail =~ s/.*<//;
		$senderemail =~ s/>.*//;
		
		#if(($totalshortname ne "myewb") && ($totalshortname ne "ewb-watchlist"))
		#{
		#	$recipients[scalar @recipients] = $senderemail;
		#	#$recipients[scalar @recipients] = 'myewb@ewb.ca';
		#}

		for($i=0; $i < @recipients; $i++)
		{
			$recipients[$i] = lc($recipients[$i]);
		}

		# sort the list by domain & remove duplicates
		@temp = sort {(reverse $a) cmp (reverse $b)} @recipients;
		$prev = "not equal to $temp[0]";
		@recipients = grep($_ ne $prev && ($prev = $_, 1), @temp);

		# For stats
		$numsentto = @recipients;

		#################
		### SEND MAIL ###
		#################

		# create a message using MIME:Lite because we need multipart
		$msg = MIME::Lite->new( 
				Type		=> 'multipart/alternative',
				Datestamp	=> 0
			);

		# attach the plaintext version
		$textattachment = MIME::Lite->new(
				Type		=> 'text/plain',
				Data		=> $textMessage,
				Encoding        => "quoted-printable"
			);
		$textattachment->attr('content-type.charset' => 'ISO-8859-1');
		$msg->attach($textattachment);

		# attach the nicely formatter version
		$htmlattachment = MIME::Lite->new(
				Type		=> 'text/html',
				Data		=> $htmlMessage,
				Encoding        => "quoted-printable"
			);
		$htmlattachment->attr('content-type.charset' => 'ISO-8859-1');
		$msg->attach($htmlattachment);

		if ($lang eq "fr")
		{
			$ewbprefix = "isf";
		}
		else
		{
			$ewbprefix = "ewb";
		}

		$toaddress = "";
		if($totalshortname)
		{
			$toaddress = $totalshortname . '@my.ewb.ca';
			if ($totalshortname eq "ewb")
			{
				$subject = "[" . $ewbprefix . "] " . $subject;
			}
			else
			{
	                        $subject = "[" . $ewbprefix . "-" . $totalshortname . "] " . $subject;
			}
		}
		elsif (@recipients == 1)
		{
			$toaddress = $recipients[0];
		}
		else
		{
			$subject = "[" . $ewbprefix . "] " . $subject;
			$toaddress = 'notices@my.ewb.ca';
		}

		# Add cc'ed recipients
		@cclist = split(',', $cc);
		for($i=0; $i < @cclist; $i++)
		{
			push(@recipients, $cclist[$i]);
		}

		@bcclist = split(',', $bcc);
		for($i=0; $i < @bcclist; $i++)
		{
			push(@recipients, $bcclist[$i]);
		}

		# create the bulkmail object to send to hundreds of people
		$bulk = Mail::Bulkmail->new(
				'LIST'		=> \@recipients,
				'Message'	=> $msg->body_as_string,
				'To'		=> $toaddress,
				'From'		=> unac_string('ISO-8859-1', $sender),
				'Sender'	=> 'mailer@ewb.ca',
				'Subject'	=> "$subject "
			) || die 'Problem setting up email: ' . Mail::Bulkmail->error();


		# hack to deal with the multi-part text stuff
		@headerinfo = split /:\s|\n/, $msg->header_as_string ;

		for (my $i = 0; $i < @headerinfo; $i+=2) 
		{
			if($headerinfo[$i] eq "Content-Type")
			{
				$headerinfo[$i] = "Content-type";
			}
			$bulk->header($headerinfo[$i], $headerinfo[$i+1]);
		}

		# send the thing!
		$bulk->bulkmail || die 'Problem sending: ' . $bulk->error;

		# Log the mail and remove from queue
		$date = localtime;
		$dbh->query("UPDATE mailer_email SET progress='sent', numsentto='$numsentto', date='$date' WHERE id='$id'");
		
		# rolling cleanup (note: fewer than 100 left after other cleanup call)
		#$deleteThreshold = $id - 1000;
                #$dbh->query("delete from email WHERE progress='sent' and id <'$deleteThreshold'");

	}

	# db cleanup 2: get rid of passwords and useless welcome emails from queue
	#$dbh->query("delete from email WHERE progress='sent' and shortname='myewb'");

	################
	### CLEAN UP ###
	################
	rename "$path/running.txt", "$path/notrunning.txt";
	#print STDOUT "Finished all emails\n";
}
else
{
	#######################
	### SECOND INSTANCE ###
	#######################

	#print STDOUT "Another instance detected...\n";
	
	open(FILEHANDLE, "< $path/running.txt");
	@info = stat FILEHANDLE;
	@moddate = localtime($info[9]);
	@nowdate = localtime();
	
	# Deal with stale instances (ie, running for over an hour)
	if(($nowdate[2] - $moddate[2]) >= 2)
	{
		# remove the marker, so the next time this script is called it will run
		rename "$path/running.txt", "$path/notrunning.txt";
		open(RESULTS, ">>  $path/lasterror.txt");
		$thestring = localtime;
		print RESULTS $thestring . "\n";
		close RESULTS;
		print STDOUT "Stale instance removed \n";
	}

}
