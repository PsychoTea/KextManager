<?php
	// KextSRV
	header("Content-Type: text/json");
	if($_GET['C'] != "KextManager") {
		die(json_encode(array("Result" => "Failed")));
	}
	
	switch($action = $_GET['A']) {
		
		case "getTotalKexts":
		echo json_encode(array("Result" => "Success", "TotalKexts" => rand()));
		break;
	
		default:
		echo json_encode(array("Result" => "Failed"));
	}

	die();
?>