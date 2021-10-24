<?php

if($_SERVER['REMOTE_ADDR']=="" and isset($_POST))
{
  if(isset($_POST['htype']) and isset($_POST['value'])) {
    include "../rb.php";

    R::setup('mysql:host=localhost;dbname=deadpool', "","");
    $stat = R::dispense("history"); 
    $stat->htype = $_POST['htype'];
    $stat->timestamp = time();
    $stat->value = $_POST['value'];
    R::store($stat);
  }
}
?>
