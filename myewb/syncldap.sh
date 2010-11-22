#!/usr/bin/php
<?php

require("settings.php");
$userid = $argv[1];

$ds = ldap_connect($ldap_server);
$r = ldap_bind($ds, $ldap_dn, $ldap_pass);

mysql_connect($mysql_server, $mysql_user, $mysql_pass);
mysql_select_db($mysql_db);

$qry = "SELECT u.id, u.first_name, u.last_name, u.email FROM auth_user u, profiles_memberprofile p WHERE p.ldap_sync=1 AND p.user2_id=u.id";
$result = mysql_query($qry);

while (list($userid, $fname, $lname, $email) = mysql_fetch_array($result))
{
	$qry2 = "SELECT address FROM networks_emailforward WHERE user_id=$userid";
	$result2 = mysql_query($qry2);
	$forwards = array();
	$num_fwds = mysql_num_rows($result2);
	while (list($fwd) = mysql_fetch_array($result2))
		$forwards[] = $fwd;

	$values["ewbMyewbID"] = $userid;
	$values["ewbMailInbox"] = $email;
	$values["cn"] = $fname;
	$values["sn"] = $lname;
	$values["objectClass"] = array("top", "ewbMailForward", "ewbPerson");
	$values["ewbMailAddress"] = $forwards;

	$sr = ldap_search($ds, "ou=people,dc=ewb,dc=ca", "(ewbMyewbID=$userid)", array("ewbMyewbID"));
	$entries = ldap_get_entries($ds, $sr);
	if ($entries['count'])
		ldap_delete($ds, "ewbMyewbID=$userid,ou=people,dc=ewb,dc=ca");

	if ($num_fwds)
	{
		ldap_add($ds, "ewbMyewbID=$userid,ou=people,dc=ewb,dc=ca", $values);
	}

	$qry = "UPDATE profiles_memberprofile SET ldap_sync=0 WHERE user2_id=$userid";
	mysql_query($qry);

	echo "Updated $uid - $fname $lname ($email)\n";
}
?>
