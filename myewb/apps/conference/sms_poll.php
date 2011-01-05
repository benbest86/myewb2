<?php

$imap = imap_open("{imap.gmail.com:993/ssl}INBOX", "sms@ewb.ca", "PASSWORD")
     or die("can't connect: " . imap_last_error());

$num = imap_num_msg($imap);

for ($i = 1; $i <= $num; $i++)
{
        $msg = imap_qprint(imap_body($imap, $i));

        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, "http://my.ewb.ca/conference/schedule/sms/stop/")
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, array('message' => $message));

        $return = curl_exec($ch);
        echo $return . "\n\n-------------------\n\n";

        imap_mail_move($imap, $i, "processed");
}

imap_close($imap);


?>
