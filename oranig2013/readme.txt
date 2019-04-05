2013 edition of ORANIG  

This zip archive contains model, data, and documentation for the
2013 version of the ORANI-G model. A number of minor improvements
have been made since the last 'official' version in 2003.

Unzip the archive into an empty new folder. Assuming that you have
some version of GEMPACK (Release 9 or later), you can build and run
the model as follows.

To build model, type from the command-line:
    tablo -pgs ORANIG

Two sample simulations are supplied. To run them, type from the
command-line:
    gemsim -cmf ORANIGSR.CMF
    gemsim -cmf ORANIGLR.CMF

Or run the file TEST.BAT to build model and run both simulations

Consult ORANIG06doc.PDF for more information.

Changes for the 2013 edition of ORANI-G
New NTB variables and location quotient display 

Changes for the 2012 edition of ORANI-G 
Change May 2012: No STI file -- condensation specified in TAB file
Addition May 2012: new variables x0gdpdif, w0gdpdif and x0gdpinca 
Addition April 2011: regx3tot variable and REGDEM coefficient 
Change Jan 2011: modified regional decompositions to add up exactly using
   multistep solutions 
Addition Oct 2007 New foreign currency export price variable pf4:
      swap with fp4 to simulate fixed export prices 
Addition Jan 2006 Post-sim section with ranked Fan decomposition 
Addition Feb 2005 Variables for back-of-the-envelope explanations of results 

Changes for the 2003 edition of ORANI-G 
This edition included new variables: p1var (short-run variable cost
price index); x0gne, p0gne and w0gne (absorption aggregates);
xgdpfac (GDP at factor cost, easily decomposed into components due
to each primary factor). New real income-side GDP variable x0gdpinc
equals x0gdpexp and can be decomposed into primary factor, tech
change and tax components. Some equations have been re- arranged to
make them more friendly to AnalyseGE. For the same reason, many
substitutions were converted to backsolves. Previously all
parameters were positive except export demand elasticities and
Frisch parameters: now these also may be positive without error. The
ID01 function is used instead of TINY in some places. TINY and ID01
appear in a few more places to combat rare zero-divide problems. New
optional labour supply functions -- search for flabsup(o).
