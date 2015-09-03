<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="2.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:output method="xml" version="1.0" encoding="utf-8" indent="yes" omit-xml-declaration="no"/>

	<xsl:template match="text()">
		<xsl:copy-of select="normalize-space(.)"/>
	</xsl:template>
	
	<xsl:template match="/">
		<documentation>
			<interfaces>
				<xsl:for-each select="//decorator[starts-with(.,'DECORATOR.interfaceFunc')]">
					<xsl:copy-of select=".."/>
				</xsl:for-each>
			</interfaces>
			<functionality>
				<xsl:for-each select="//decorator[.='test']/../..">
					<applicationfunction>
						<xsl:attribute name="name">
							<xsl:copy-of select="
								string-join(
									(
										substring(./@name,1,1),
										substring(
											lower-case(
												replace(
													substring-before(./@name,'Test'),
													'([A-Z])',
													' $0'								
												)
											),
											3
										)
									),
									''
								)
							"/>
						</xsl:attribute>
						<xsl:for-each select="method[@name!='setUp' and @name != 'tearDown' and not(starts-with(@name,'_'))]">
							<facet>
								<xsl:copy-of select="@name"/>
								<xsl:apply-templates select="text()"/>
							</facet>
						</xsl:for-each>
					</applicationfunction>
				</xsl:for-each>
				<xsl:variable name="jsunit" select="document('../../doc/screenshots/unittests.xml')"/>
				<applicationfunction name="JavaScript tests">
					<xsl:for-each select="$jsunit//testcase">
						<facet>
							<xsl:copy-of select="@name"/>
						</facet>
					</xsl:for-each>
				</applicationfunction>
			</functionality>
		</documentation>
	</xsl:template>
</xsl:stylesheet>

