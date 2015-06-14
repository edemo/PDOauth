<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="2.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:output method="xml" version="1.0" encoding="utf-8" indent="yes" omit-xml-declaration="yes"/>
	
	<xsl:template match="commitlog">
		<article>
			<title>PDOauth history</title>
			<table>
				<title>commits</title>
				<tgroup cols="4">
					<thead>
						<row>
							<entry>Commit id</entry>
							<entry>Author</entry>
							<entry>Date</entry>
							<entry>Commit message</entry>
						</row>
					</thead>
					<tbody>
				    	<xsl:apply-templates select="*"/>
					</tbody>
				</tgroup>
			</table>
		</article>
	</xsl:template>

	<xsl:template match="commit">
		<row>
		<entry><xsl:value-of select="@id"/></entry>
		<entry><xsl:value-of select="@author"/></entry>
		<entry><xsl:value-of select="@date"/></entry>
		<entry><xsl:value-of select="."/></entry>
		</row>
	</xsl:template>
	
	<xsl:template match="text()">
		<xsl:copy-of select="normalize-space(.)"/>
	</xsl:template>
	
</xsl:stylesheet>

