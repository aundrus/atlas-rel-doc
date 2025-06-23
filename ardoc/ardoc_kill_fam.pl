#!/usr/bin/env perl
use Env;
use Cwd;
use subs qw/get_pids/;

sub get_pids {

    my($procs, @kids) = @_;

    my @pids;
    foreach my $kid (@kids) {
       foreach my $proc (@$procs) {
           if ($proc->{'ppid'} == $kid && $proc->{'pgid'} == $group_id ) {
#	   if ($proc->{'ppid'} == $kid ) {
               my $pid = $proc->{'pid'};
#               print " FFFF $pid \n";
               push @pids, $pid, get_pids $procs, $pid;
           }
       }
    }
    @pids;
}


if ($#ARGV < 1) {
    print "ardoc_kill_fam: arguments required: process number(s), signal \n";
    exit 1;}

my $signal = $ARGV[$#ARGV];
$fields = $#ARGV - 1; 

if ( $signal < 0 || $signal > 15 ) { 
   print "ardoc_kill_fam: signal (last argument) must be between 0 and 15 \n";
   exit 1;}

for ($mmm=0; $mmm <= $fields; $mmm++){

my $procnum = $ARGV[$mmm];
print "ardoc_kill_fam: handling process $procnum ... \n";
my $UID = $>;
$group_id;
my @pids;
my @procs1=();
push @pids, $procnum;

@output=`ps -ww -u $UID  -o pid,ppid,pgid,args`;

#foreach $proc (@output)
#{print "AAA $proc \n";} 

foreach $line (@output)
{
    @fields = split(" ", $line);
    $apid = $fields[0];
    next if ( $apid eq "PID");
    $appid = $fields[1];
    $apgid = $fields[2]; 
    if ( $apid == $procnum ){$group_id = $apgid;}
    @aarg=();
	for ($m=3; $m <= $#fields; $m++){
	    push(@aarg, $fields[$m]);
	}
    $entry1={};
    $entry1->{'pid'}=$apid;
    $entry1->{'ppid'}=$appid;
    $entry1->{'pgid'}=$apgid;
    $entry1->{'args'}=@aarg;
    @kd=();  
          foreach $line1 (@output)
          {
              @fields = split(" ", $line1);
	      $apidk = $fields[0];
              $appidk = $fields[1];
	      next if ( $appidk ne $apid );
	      push(@kd, $apidk);
           }  
    $entry{'kids'}=[ @kd ];
    $entry1->{'kids'}=[ @kd ];
#    print "SDD $procnum $apid $appid $apgid $entry1->{'pid'} \n " ;
#    print "KDD @kd @{$entry1->{'kids'}}\n";
    push(@procs1,$entry1); 
}

#foreach $proc1 (@procs1)
#{$a=$proc1{'pid'};
#print "OOOO $proc1->{'pid'} \n";
# @df=@{$proc1->{'kids'}};
#print "OOAA @df \n";
#}
#print "GID $group_id\n";

my(@procs)=@procs1;
my(@kids) = get_pids \@procs, @pids;

@pids = (@pids, @kids);
foreach $k (@pids)
{print "ardoc_kill_fam: killing $k with signal $signal \n";
#system("kill -9 $k"); 
}
#print "IDS $) xxx $> xxx $<\n";

kill $signal, @pids;
}
