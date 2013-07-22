#
# http cURL wrapper for CUBE
#
#

use strict;
use warnings;



my $_sUsage = <<END;
####################################################################################################

	Usage:

		cube PORT get PATH
		cube PORT post PATH
		cube PORT put PATH

		cube 11111 get gc/games
		cube 11111 get gc/games/1
		cube 11111 post gc/games name=foo

####################################################################################################
END




################################################################################
sub main(@) {

	my $port = shift || die "Missing PORT";
	if (!($port =~ /^\d+$/))  {die "PORT not numeric";}

  	my $cmd = shift || die "Missing COMMAND";
	$cmd = uc $cmd;

 	my $path = shift || die "Missing PATH";

	my $arg = shift || '';

	system("curl --silent -X $cmd http://localhost:$port/$path $arg | python -mjson.tool");
}




main(@ARGV);





