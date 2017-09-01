<?php
	/*
	 * Validate client certificate
	 * 
	 */
?>
<html>
	<head>
	<?php
		/**
		 * 
		 * Multi-factor SSL client certificate validation
		 * 
		 **/
		function hasValidCert()
		{
				if (!isset($_SERVER['SSL_CLIENT_M_SERIAL'])
					|| !isset($_SERVER['SSL_CLIENT_V_END'])
					|| !isset($_SERVER['SSL_CLIENT_VERIFY'])
					|| $_SERVER['SSL_CLIENT_VERIFY'] !== 'SUCCESS'
					|| !isset($_SERVER['SSL_CLIENT_I_DN'])
				) {
					echo "No valid certificate found(1).<br>";
					exit();
				}
		 
				if ($_SERVER['SSL_CLIENT_V_REMAIN'] <= 0) {
					echo "No valid certificate found(2).<br>";
					exit();
				}
			echo "Valid certificate found!<br>";
		}

		/**
		 * 
		 * Stream certificate information into an array.
		 * 
		 **/
		function streamCert() 
		{
			$SSLclient = NULL;
			$SSLclient = array();
			
			while (list($key,$value) = each($_SERVER)) {
				if (strpos($key, 'SSL_CLIENT') !== false) {
					$SSLclient[$key]=  $value;
				}
			}
			return $SSLclient;
		}

		/**
		 *
		 * Debugging
		 *
		 **/
		function deBug()
		{	
			echo "<pre>";
			while(list($key,$value) = each($_SERVER)) {
				if (strpos($key, 'SSL_') !== false) {
					echo $key . "=>" . $value . "<br/>";
				}
			}
			echo "</pre>";
			exit();
		}
	?>
	</head>
	<body>
		<?php
			if (isset($_GET['debug'])){
				deBug();
			} else if (isset($_GET['skip'])){
				$SSLclient = streamCert();
			} else {
				hasValidCert();
				$SSLclient = streamCert();
			}
		?>
		<center>
			<table border="1" width="50%">
				<tr><td><strong>Attribute</strong></td><td><strong>Value</strong></td></tr>
				<?php
					foreach($SSLclient as $key=>$value) {
						echo '<tr><td>' . $key . '</td><td>' . $value . '</td></tr>';
					}
				?>
			</table>
			<br/>
			<?php
				session_start();
				$client = array_keys($SSLclient, "SSL_CLIENT_S_DN_EMAILADDRESS");
				$_SESSION['totpUser'] = $client;
			?>
			Login successfull for client <?php $client ?><br/><br/>
			<a href=/TOTP/auUser.php><b>Continue</b></a>
		</center>
	</body>
</html>
