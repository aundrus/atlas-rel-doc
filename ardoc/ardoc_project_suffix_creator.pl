#!/usr/bin/env perl
use Env;

my $ARDOC_SUFFIX_PREPEND="$ARDOC_SUFFIX_PREPEND";
my $ARDOC_ARCH="$ARDOC_ARCH";
my $ARDOC_PROJECT_NAME="$ARDOC_PROJECT_NAME";
my $ARDOC_HOME="$ARDOC_HOME";

$full_name="$ARDOC_PROJECT_NAME";
@fields = split("-", $ARDOC_ARCH);
$machine="";
for ($m=0; $m <= $#fields; $m++){
 if ( $fields[$m] =~ i686 || $fields[$m] =~ ia32 ) { $machine="32B"; last;}
 if ( $fields[$m] =~ x86_64 || $fields[$m] =~ amd64 ) { $machine="64B"; last;} 
 if ( $fields[$m] =~ aarch64 ) { $machine="ARM64B"; last;}
}

$opsyst="";
for ($m=0; $m <= $#fields; $m++){
 if ( $fields[$m] =~ slc3 ) { $opsyst="S3"; last;}
 if ( $fields[$m] =~ slc4 ) { $opsyst="S4"; last;}
 if ( $fields[$m] =~ slc5 ) { $opsyst="S5"; last;}
 if ( $fields[$m] =~ slc6 ) { $opsyst="S6"; last;}
 if ( $fields[$m] =~ cc7 ) { $opsyst="C7"; last;}
 if ( $fields[$m] =~ centos7 ) { $opsyst="C7"; last;}
 if ( $fields[$m] =~ centos9 ) { $opsyst="C9"; last;}
 if ( $fields[$m] =~ el9 ) { $opsyst="E9"; last;}
 if ( $fields[$m] =~ mac104 ) { $opsyst="M104"; last;}
 if ( $fields[$m] =~ mac105 ) { $opsyst="M105"; last;}
 if ( $fields[$m] =~ mac106 ) { $opsyst="M106"; last;}
 if ( $fields[$m] =~ mac107 ) { $opsyst="M107"; last;}
 if ( $fields[$m] =~ mac108 ) { $opsyst="M108"; last;}
 if ( $fields[$m] =~ mac109 ) { $opsyst="M109"; last;}
 if ( $fields[$m] =~ mac1010 ) { $opsyst="M1010"; last;}
}


for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ gcc46 ) { $opsyst="${opsyst}G46"; last;}
    elsif ( $fields[$m] =~ gcc47 ) { $opsyst="${opsyst}G47"; last;}
    elsif ( $fields[$m] =~ gcc48 ) { $opsyst="${opsyst}G48"; last;}
    elsif ( $fields[$m] =~ gcc49 ) { $opsyst="${opsyst}G49"; last;}
    elsif ( $fields[$m] =~ gcc45 ) { $opsyst="${opsyst}G45"; last;}
    elsif ( $fields[$m] =~ gcc4 ) { $opsyst="${opsyst}G4"; last;}
    elsif ( $fields[$m] =~ gcc61 ) { $opsyst="${opsyst}G61"; last;} 
    elsif ( $fields[$m] =~ gcc62 ) { $opsyst="${opsyst}G62"; last;}
    elsif ( $fields[$m] =~ gcc8 ) { $opsyst="${opsyst}G8"; last;}
    elsif ( $fields[$m] =~ gcc9 ) { $opsyst="${opsyst}G9"; last;}
    elsif ( $fields[$m] =~ gcc10 ) { $opsyst="${opsyst}G10"; last;}
    elsif ( $fields[$m] =~ gcc11 ) { $opsyst="${opsyst}G11"; last;}
    elsif ( $fields[$m] =~ gcc12 ) { $opsyst="${opsyst}G12"; last;}
    elsif ( $fields[$m] =~ gcc13 ) { $opsyst="${opsyst}G13"; last;}
    elsif ( $fields[$m] =~ gcc14 ) { $opsyst="${opsyst}G14"; last;}
    elsif ( $fields[$m] =~ gcc15 ) { $opsyst="${opsyst}G15"; last;}
}

for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ icc ) { $opsyst="${opsyst}IC"; last;}
}

for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ /^.*clang3[0123456].*$/ ) { $opsyst="${opsyst}C3"; last;}
}
for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ /^.*clang37.*$/ ) { $opsyst="${opsyst}C37"; last;}
}
for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ /^.*clang38.*$/ ) { $opsyst="${opsyst}C38"; last;}
}
for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ /^.*clang39.*$/ ) { $opsyst="${opsyst}C39"; last;}
}

for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ /^.*clang5.*$/ ) { $opsyst="${opsyst}C5"; last;}
}

for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ /^.*clang6.*$/ ) { $opsyst="${opsyst}C6"; last;}
}

for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ /^.*clang7.*$/ ) { $opsyst="${opsyst}C7"; last;}
}

for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ /^.*clang8.*$/ ) { $opsyst="${opsyst}C8"; last;}
}

for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ /^.*clang9.*$/ ) { $opsyst="${opsyst}C9"; last;}
}

for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ /^.*clang10.*$/ ) { $opsyst="${opsyst}C10"; last;}
}

for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ /^.*clang15.*$/ ) { $opsyst="${opsyst}C15"; last;}
}

for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ /^.*clang16.*$/ ) { $opsyst="${opsyst}C16"; last;}
}

for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ /^.*clang17.*$/ ) { $opsyst="${opsyst}C17"; last;}
}

for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ /^.*clang18.*$/ ) { $opsyst="${opsyst}C18"; last;}
}

for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ /^.*clang19.*$/ ) { $opsyst="${opsyst}C19"; last;}
}

for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ /^.*clang20.*$/ ) { $opsyst="${opsyst}C20"; last;}
}

for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ llvm ) { $opsyst="${opsyst}VM"; last;}
}

$opt="";
for ($m=0; $m <= $#fields; $m++){
    if ( $fields[$m] =~ opt ) { $opt="Opt"; last;}
    if ( $fields[$m] =~ dbg ) { $opt="Dbg"; last;}
}

print "${ARDOC_SUFFIX_PREPEND}${machine}${opsyst}${full_name}${opt}";
exit;
