<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="2.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:output method="xml" version="1.0" encoding="utf-8" indent="yes" omit-xml-declaration="yes"/>

	<xsl:template match="text()">
		<xsl:copy-of select="normalize-space(.)"/>
	</xsl:template>
	
	<xsl:template match="/">
		<documentation>
			<interfaces>
				<xsl:for-each select="//decorator[starts-with(.,'app.route')]">
					<xsl:copy-of select=".."/>
				</xsl:for-each>
			</interfaces>
			<functionality>
				<xsl:for-each select="//decorator[.='test']/../..">
					<ApplicationFunction>
						<xsl:attribute name="name">
							<xsl:copy-of select="substring-before(./@name,'Test')"/>
						</xsl:attribute>
						<xsl:for-each select="Method[@name!='setUp']">
							<facet>
								<xsl:copy-of select="@name"/>
								<xsl:apply-templates select="text()"/>
							</facet>
						</xsl:for-each>
					</ApplicationFunction>
				</xsl:for-each>
			</functionality>
		</documentation>
	</xsl:template>
</xsl:stylesheet>

