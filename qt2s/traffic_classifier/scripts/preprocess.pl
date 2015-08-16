#!/usr/bin/perl
# Preprocess Doha traffic tweets and substitutes local entities by keywords
# Francisco Guzman
# (c) QCRI, 2015
binmode(STDIN, ":utf8");
binmode(STDOUT,":utf8");

while(<>){ 
	#s/ +/\n/g; 
	#remove hashtags
	chomp;
	my $text=$_;
	$text=cleanText($text);


	print $text."\n"; 
}

sub cleanText()
{
	my $text = shift;
	$text =~ s/\#//g; 
	#lowercase
	$text = lc($text);
	#substitute retional news outlet
	$text =~ s/\@?(dohanews|gulftimes_qatar|alrayyantv|peninsula_qatar|qfradio2|qatarliving|iloveqatar)/\$\$regional_news\$\$/g;
	#substitute government entities
	$text =~ s/\@?(moi_qatar(en)?|ashghal)/\$\$govt_entity\$\$/g;
	#substitute cities
	$text =~ s/(doha|dubai|dukhan|(al[-\s]?)?(khor|rayyan|jumayl|wakra(h)?)|abudhabi)/\$\$my_city\$\$/gi;
	#substitute country
	$text =~ s/(qatar|uae)/\$\$my_country\$\$/g;
	$text =~ s/(sandstorm|wind|rain|thunderstorm|storm|dust)(s|y)?/\$\$weather\$\$/g;
	#substitute region
	$text =~ s/(gulf|gcc)/\$\$my_region\$\$/gi;
	$text =~ s/https?\:\/\/[^ ]+[\s\n]?/\$\$url\$\$/g; 
	$text =~ s/(\$\$(\S+?)\$\$)/ \1 /g;
	#join several tags
	$text =~ s/_+/_/g; 
	$text =~ s/ _/ /g;
	return $text;

}