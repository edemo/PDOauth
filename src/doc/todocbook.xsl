<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="2.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:output method="xml" version="1.0" encoding="utf-8" indent="yes" omit-xml-declaration="yes"/>
	
	<xsl:variable name="buildinfo" select="document('../../doc/xml/buildinfo.xml')"/>
	<xsl:template match="documentation">
		<article>
			<title>PDOauth documentation</title>
			<variablelist>
				<varlistentry>
					<term>Branch:</term>
					<listitem><xsl:value-of select="$buildinfo//branch"/></listitem>
				</varlistentry>
				<varlistentry>
					<term>Commit:</term>
					<listitem><xsl:value-of select="$buildinfo//commit"/></listitem>
				</varlistentry>
				<varlistentry>
					<term>Build:</term>
					<listitem><xsl:value-of select="$buildinfo//build"/></listitem>
				</varlistentry>
			</variablelist>
			<para>
				See commit log <ulink url="commitlog.html">here</ulink>.
			</para>
		      <xsl:apply-templates select="*"/>
		</article>
	</xsl:template>

	<xsl:template match="interfaces">
		<section>
			<title>Interfaces</title>
		    <xsl:apply-templates select="*"/>
		</section>
	</xsl:template>
	
	<xsl:template match="functionality">
		<section>
			<title>Functionality</title>
		      <xsl:apply-templates select="*"/>
		</section>
	</xsl:template>

	<xsl:template match="function">
		<section>
			<title><xsl:value-of select="@name"/></title>
		    <xsl:apply-templates select="decorator"/>
		    <xsl:apply-templates select="text()"/>
		</section>
	</xsl:template>
	
	<xsl:template match="decorator">
		<para>
			<xsl:value-of select="."/>
		</para>
	</xsl:template>

	<xsl:template match="applicationfunction">
		<section>
			<title><xsl:value-of select="@name"/></title>
			<itemizedlist>
			    <xsl:apply-templates select="facet"/>
		    </itemizedlist>
		</section>
	</xsl:template>

	<xsl:template match="facet">
		<listitem>
			<xsl:variable name="commaed" select="replace(@name,'__',',')"/>
			<xsl:variable name="spaced" select="replace($commaed,'_',' ')"/>
			<xsl:variable name="capitalized" select="
				concat(upper-case(substring($spaced,1,1)),
          			substring($spaced, 2),
          			' '[not(last())]
         		)
  			"/>
			<xsl:value-of select="$capitalized"/>.<xsl:value-of select="text()"/>
		</listitem>
	</xsl:template>
	
	<xsl:template match="text()">
		<xsl:copy-of select="normalize-space(.)"/>
	</xsl:template>
	
</xsl:stylesheet>

