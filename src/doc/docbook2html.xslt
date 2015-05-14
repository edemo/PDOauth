<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version='2.0'
                xmlns="http://www.w3.org/TR/xhtml1/transitional"
								xmlns:fn="http://www.w3.org/2005/xpath-functions"
                exclude-result-prefixes="#default">


<xsl:import href="/usr/share/xml/docbook/stylesheet/docbook-xsl/xhtml/docbook.xsl"/>

<xsl:output method="xhtml" version="1.1" encoding="utf-8" indent="yes" omit-xml-declaration="no"/>

<xsl:param name="toc.section.depth">3</xsl:param>
<xsl:param name="html.stylesheet">../static/docbook.css</xsl:param>
<xsl:param name="generate.toc">
appendix  toc,title
article/appendix  nop
article   toc,title,figure
book      toc,title,figure,table,example,equation
chapter   toc,title
part      toc,title
preface   toc,title
qandadiv  toc
qandaset  toc
reference toc,title
sect1     toc
sect2     toc
sect3     toc
sect4     toc
sect5     toc
section   toc
set       toc,title
</xsl:param>
<!-- Add other variable definitions here -->

</xsl:stylesheet>


