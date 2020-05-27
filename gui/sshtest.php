<?php

$methods = array(
  'kex' => 'diffie-hellman-group1-sha1',
  'client_to_server' => array(
    'crypt' => '3des-cbc',
    'comp' => 'none'),
  'server_to_client' => array(
    'crypt' => 'aes256-cbc,aes192-cbc,aes128-cbc',
    'comp' => 'none'));

$callbacks = array('disconnect' => 'my_ssh_disconnect');

$connection = ssh2_connect('10.222.248.234', 22);
ssh2_auth_password($connection, 'admin', 'admin*1');

$ssh_stream = ssh2_exec($connection, 'uptime');

stream_set_blocking($ssh_stream, true);

while ($f = fgets($ssh_stream)) {
  echo  $f;
}

fclose($ssh_stream);
  

// if($stream = ssh2_exec($connection, 'df -h')) {
// stream_set_blocking($stream, true);
// echo stream_get_contents($stream);
// }

?>
