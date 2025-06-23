#!/usr/bin/env perl
use Env;
use File::Basename;
if ($#ARGV != 0) {
    print " unit_test_log_processor: Error: one arg req: file name \n";
    exit 1;}
if ( $WORKSPACE eq "" ) {
    print " unit_test_log_processor: Error: WORKSPACE not defined \n"; 
    exit 1;}
if ( ! -d $WORKSPACE ) {
    print " unit_test_log_processor: Error: WORKSPACE $WORKSPACE does not exist \n";
    exit 1;}

$file = $ARGV[0];
if ( ! -f $file ) {
    print " unit_test_log_processor: Error: file $file does not exist \n";
    exit 1;}
$file_base=basename($file);
$copy_file="${WORKSPACE}/${file_base}_copy";
print " unit_test_log_processor: Info: copy $file $copy_file \n";
system("cp -Rp $file $copy_file");
open(WRITEDATA,">$file");
open(FILE,"<$copy_file");

open(FILE,"<$copy_file");
$nrec = 0;
$sign = 0;
    while (<FILE>)
{
    $nrec++;
    chomp;
#    next if ($_ =~ /^#/ );
#    next if (length($_) eq 0);
    ( $trim1 = $_ ) =~ s/^\s+//;
    ( $trim2 = $trim1 ) =~ s/\s+$//;
#    print "TRIM2 $trim2 $sign\n";
    if ( $sign == 0 ) 
    {
       if ( $trim2 =~ /^\[ERROR_MESSAGE\]$/ )
       {
        $sign=1;
       }
       else
       {
	print WRITEDATA "$_\n";
       }
    } 
    else
    {
       if ( $_ =~ /^No\s+tests\s+were\s+found.*$/ )
       {
	 print WRITEDATA "[MINOR_WARNING_MESSAGE]\n";
         print WRITEDATA "$_\n";
       }
       else
       {
	   print WRITEDATA "[ERROR_MESSAGE]\n";
	   print WRITEDATA "$_\n";
       }
       $sign=0; 
    } 
}
if ( -f $copy_file ){ unlink "$copy_file"; }
