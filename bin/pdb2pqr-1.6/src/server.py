"""
    CGI Server for PDB2PQR

    This module contains the various functions necessary to run PDB2PQR
    from a web server.

    ----------------------------
   
    PDB2PQR -- An automated pipeline for the setup, execution, and analysis of
    Poisson-Boltzmann electrostatics calculations

	Copyright (c) 2002-2010, Jens Erik Nielsen, University College Dublin; 
	Nathan A. Baker, Washington University in St. Louis; Paul Czodrowski & 
	Gerhard Klebe, University of Marburg

	All rights reserved.

	Redistribution and use in source and binary forms, with or without modification, 
	are permitted provided that the following conditions are met:

		* Redistributions of source code must retain the above copyright notice, 
		  this list of conditions and the following disclaimer.
		* Redistributions in binary form must reproduce the above copyright notice, 
		  this list of conditions and the following disclaimer in the documentation 
		  and/or other materials provided with the distribution.
		* Neither the names of University College Dublin, Washington University in 
		  St. Louis, or University of Marburg nor the names of its contributors may 
		  be used to endorse or promote products derived from this software without 
		  specific prior written permission.

	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
	ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
	WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
	IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
	INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
	BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, 
	DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF 
	LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE 
	OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED 
	OF THE POSSIBILITY OF SUCH DAMAGE.

    ----------------------------
"""

import os
import string
import sys
import time

from aconf import *

__date__ = "4 August 2008"
__author__ = "Todd Dolinsky, Samir Unni, Yong Huang"

# GLOBAL SERVER VARIABLES
""" The absolute path to root HTML directory """
""" The relative path to results directory from script directory.
    The web server (i.e. Apache) MUST be able to write to this directory. """
TMPDIR = "tmp/"
""" The maximum size of temp directory (in MB) before it is cleaned """
LIMIT = 500.0
""" The path to the web site *directory* """
""" The name of the main server page """
WEBNAME = "index.html"
""" The stylesheet to use """
STYLESHEET = WEBSITE + "pdb2pqr.css"
""" The refresh time (in seconds) for the progress page """
REFRESHTIME = 20
""" The absolute path to the loadavg file - set to "" or None if
    not to be included """
LOADPATH = "/proc/loadavg"
""" The path to the pdb2pqr log - set to "" or None if not to be
    included.  The web server (i.e. Apache) MUST be able to write to
    this directory. """
LOGPATH = "%s/%s/usage.txt" % (INSTALLDIR, TMPDIR)


def setID(time):
    """
    Given a floating point time.time(), generate an ID.
    Use the tenths of a second to differentiate.

    Parameters
        time:  The current time.time() (float)
    Returns
        id  :  The file id (string)
    """
    strID = "%s" % time
    period = string.find(strID, ".")
    id = "%s%s" % (strID[:period], strID[(period + 1) : (period + 2)])
    return id


def logRun(options, nettime, size, ff, ip):
    """
    Log the CGI run for data analysis.  Log file format is as follows:

    DATE  FF  SIZE  OPTIONS   TIME

    Parameters
        options: The options used for this run (dict)
        nettime: The total time taken for the run (float)
        size:    The final number of non-HETATM atoms in the PDB file (int)
        ff:      The name of the ff used
        ip:      The ip address of the user
    """
    if LOGPATH in ("", None):
        return
    date = time.asctime(time.localtime())
    debump = 0
    opt = 0
    propka = 0
    file = open(LOGPATH, "a")

    if "ffout" in options:
        ffout = options["ffout"]
    else:
        ffout = "internal"

    text = "%s\t%s\t%s\t%s\t" % (date, ip, ff, ffout)

    opts = ""
    if "debump" in options:
        opts += "debump,"
    if "opt" in options:
        opts += "optimize,"
    if "ph" in options:
        opts += "propka,"
    if "ligand" in options:
        opts += "ligand,"
    if "apbs" in options:
        opts += "apbs,"
    if "chain" in options:
        opts += "chain,"

    if opts == "":
        opts = "none,"

    text += "%s\t%s\t%.2f\n" % (opts[:-1], size, nettime)
    file.write(text)
    file.close()


def cleanTmpdir():
    """
    Clean up the temp directory for CGI.  If the size of the directory
    is greater than LIMIT, delete the older half of the files.  Since
    the files are stored by system time of creation, this is an
    easier task.
    """
    newdir = []
    size = 0.0
    count = 0
    path = INSTALLDIR + TMPDIR

    dir = os.listdir(path)
    for filename in dir:
        size = size + os.path.getsize("%s%s" % (path, filename))
        period = string.find(filename, ".")
        id = filename[:period]
        if id not in newdir:
            newdir.append(id)
            count += 1

    newdir.sort()
    size = size / (1024.0 * 1024.0)

    newcount = 0
    if size >= LIMIT:
        for filename in newdir:
            if newcount > count / 2.0:
                break
            try:
                os.remove("%s%s.pqr" % (path, filename))
            except OSError:
                pass
            try:
                os.remove("%s%s.in" % (path, filename))
            except OSError:
                pass
            try:
                os.remove("%s%s.html" % (path, filename))
            except OSError:
                pass
            newcount += 1




# def printAcceptance(name):
#    """
#        Print the first message to stdout (web browser) - set the
#        refresh to the <id>-tmp.html file.
#
#        Parameters
#            name:    The ID of the HTML page to redirect to (string)
#    """
#    waittime = int(REFRESHTIME/2.0)
#    print "Content-type: text/html\n"
#    print "<HTML>"
#    print "<HEAD>"
#    print "<TITLE>PDB2PQR Progress</TITLE>"
#    print "<link rel=\"stylesheet\" href=\"%s\" type=\"text/css\">" % STYLESHEET
#    print "<meta http-equiv=\"Refresh\" content=\"%s; url=%s%s%s-tmp.html\">" % \
#          (waittime, WEBSITE, TMPDIR, name)
#    print "</HEAD>"
#    print "<BODY>"
#    print "<H2>PDB2PQR Progress</H2><P>"
#    print "The PDB2PQR server is generating your results - this page will automatically "
#    print "refresh every %s seconds.<P>" % REFRESHTIME
#    print "Thank you for your patience!<P>"
#
#    print "Server Information:<P>"
#    print "<blockquote>"
#    loads = getLoads()
#    if loads != None:
#        print "<font size=2>Server load:</font> <code>%s (1min)  %s (5min)  %s (15min)</code><BR>" % (loads[0], loads[1], loads[2])
#
#    print "<font size=2>Server time:</font> <code>%s</code><BR>" % (time.asctime(time.localtime()))
#    print "</blockquote>"
#
#    print "</BODY></HTML>"

# def printRedirector(name, have_opal):
#    """
#        Prints a page which redirects the user to querystatus.cgi
#    """
#
#    print "Content-type: text/html \n"
#    print "<html>"
#    print "<head>"
#    print "<meta http-equiv=\"Refresh\" content=\"0; url=%squerystatus.cgi?jobid=%s&haveopal=", % (WEBSITE, name)
#    if have_opal:
#        print "true",
#    else:
#        print "false",
#    print "\">"
#    print "</head>"
#    print "</html>"



def createResults(header, input, name, time, missedligands=None):
    """
    Create the results web page for CGI-based runs

    Parameters
        header: The header of the PQR file (string)
        input:   A flag whether an input file has been created (int)
        tmpdir:  The resulting file directory (string)
        name:    The result file root name, based on local time (string)
        time:    The time taken to run the script (float)
        missedligands: A list of ligand names whose parameters could
                 not be assigned. Optional. (list)
    """
    if missedligands is None:
        missedligands = []
    newheader = string.replace(header, "\n", "<BR>")
    newheader = string.replace(newheader, " ", "&nbsp;")

    filename = "%s%s%s.html" % (INSTALLDIR, TMPDIR, name)
    file = open(filename, "w")

    file.write("<html>\n")
    file.write("<head>\n")
    file.write("<title>PDB2PQR Results</title>\n")
    file.write('<link rel="stylesheet" href="%s" type="text/css">\n' % STYLESHEET)
    file.write("</head>\n")

    file.write("<body>\n")
    file.write("<h2>PDB2PQR Results</h2>\n")
    file.write("<P>\n")
    file.write(
        "Here are the results from PDB2PQR.  The files will be available on the "
    )
    file.write(
        "server for a short period of time if you need to re-access the results.<P>\n"
    )

    file.write('<a href="%s%s%s.pqr">%s.pqr</a><BR>\n' % (WEBSITE, TMPDIR, name, name))
    if input:
        file.write(
            '<a href="%s%s%s.in">%s.in</a><BR>\n' % (WEBSITE, TMPDIR, name, name)
        )
    pkaname = "%s%s%s.propka" % (INSTALLDIR, TMPDIR, name)
    if os.path.isfile(pkaname):
        file.write(
            '<a href="%s%s%s.propka">%s.propka</a><BR>\n'
            % (WEBSITE, TMPDIR, name, name)
        )
    typename = "%s%s%s-typemap.html" % (INSTALLDIR, TMPDIR, name)
    if os.path.isfile(typename):
        file.write(
            '<a href="%s%s%s-typemap.html">%s-typemap.html</a><BR>\n'
            % (WEBSITE, TMPDIR, name, name)
        )
    file.write(
        "<P>The header for your PQR file, including any warnings generated, is:<P>\n"
    )
    file.write("<blockquote><code>\n")
    file.write("%s<P>\n" % newheader)
    file.write("</code></blockquote>\n")
    if missedligands != []:
        file.write("The forcefield that you have selected does not have ")
        file.write(
            "parameters for the following ligands in your PDB file.  Please visit "
        )
        file.write(
            '<a href="http://davapc1.bioch.dundee.ac.uk/programs/prodrg/">PRODRG</a> '
        )
        file.write(
            "to convert these ligands into MOL2 format.  This ligand can the be "
        )
        file.write(
            "parameterized in your PDB2PQR calculation using the PEOE_PB methodology via "
        )
        file.write(
            "the 'Assign charges to the ligand specified in a MOL2 file' checkbox:<P>\n"
        )
        file.write("<blockquote><code>\n")
        for item in missedligands:
            file.write("%s<BR>\n" % item)
        file.write("<P></code></blockquote>\n")
    file.write(
        'If you would like to run PDB2PQR again, please click <a href="%s%s">\n'
        % (WEBSITE, WEBNAME)
    )
    file.write("here</a>.<P>\n")
    file.write(
        'If you would like to run APBS with these results, please click <a href="%s../apbs/index.py?pdb2pqr-id=%s">here</a>.<P>\n'
        % (WEBSITE[:-1], name)
    )
    file.write("<P>Thank you for using the PDB2PQR server!<P>\n")
    file.write(
        '<font size="-1"><P>Total time on server: %.2f seconds</font><P>\n' % time
    )
    file.write(
        '<font size="-1"><CENTER><I>Last Updated %s</I></CENTER></font>\n' % __date__
    )
    file.write("</body>\n")
    file.write("</html>\n")


def createError(name, details):
    """
    Create an error results page for CGI-based runs

    Parameters
        name:    The result file root name, based on local time (string)
        details: The details of the error (string)
    """
    filename = "%s%s%s.html" % (INSTALLDIR, TMPDIR, name)
    file = open(filename, "w")

    file.write("<html>\n")
    file.write("<head>\n")
    file.write("<title>PDB2PQR Error</title>\n")
    file.write('<link rel="stylesheet" href="%s" type="text/css">\n' % STYLESHEET)
    file.write("</head>\n")

    file.write("<body>\n")
    file.write("<h2>PDB2PQR Error</h2>\n")
    file.write("<P>\n")
    file.write("An error occurred when attempting to run PDB2PQR:<P>\n")
    file.write("%s<P>\n" % details)
    file.write(
        "If you believe this error is due to a bug, please contact the server administrator.<BR>\n"
    )
    file.write(
        'If you would like to try running PDB2QR again, please click <a href="%s%s">\n'
        % (WEBSITE, WEBNAME)
    )
    file.write("here</a>.<P>\n")
    file.write(
        '<font size="-1"><CENTER><I>Last Updated %s</I></CENTER></font>\n' % __date__
    )
    file.write("</body>\n")
    file.write("</html>\n")


