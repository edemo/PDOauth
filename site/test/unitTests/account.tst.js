QUnit.module( "User commands" ); 
QUnit.test( "InitiateResendRegistrationEmail() should initiate resend the email ", function( assert ) {
		// Initializing the test		
	pageScript = new PageScript(test)
	var testUri = test.uribase+"/v1/send_verify_email",
		testMethod = "GET",
		testText = '{"message": "email sent"}',
		checkCallback = pageScript.doLoadHome,
		checkData = 'email sent';
	pageScript.ajaxget = mockAjaxget(200,testText) // if no error
		// calling the unit	
	pageScript.InitiateResendRegistrationEmail();
		// asserts 
	assert.equal(pageScript.uri, testUri, "uri should be '/v1/send_verify_email'" );
	assert.equal(pageScript.method, testMethod, "method should be 'GET'" );
	assert_IsMessageBoxShown( assert );
	assert.ok( doesMessageContainerContain( checkData ), "the message div should contain the message of the server" );
});
