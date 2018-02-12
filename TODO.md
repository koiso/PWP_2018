
 # GENERAL SUGESTION FOR THE COURSE
 - Consider avoiding hypermedia types at the begining: they just need to provide links with link: href/rel/method (semantic descriptor).
	- The format of the response must be defined in profiles: 
		-link relations. Expected format of the request (PUT / POST / DELETE) / link to a resource. Or use HAL and only HAL.
		-application descriptor. Meaning of the different elements. You can use a subset of schema.org.
 - Possible suggestion if this is not workign in 2016. Change to JSON_LD and check if Hydra is viable. Perhaps, it is better than using profiles and media type for example) We restrict a lot the format of the data. Check http://www.slideshare.net/lanthaler/jsonld-for-restful-services and http://www.slideshare.net/lanthaler/hydra-a-vocabulary-for-hypermediadriven-web-apis. Specially nice the slide of what it has been done. Include self-descriptive lenguages. Hydra has a really nice console for documentation. Explain them that with Hydra tools will generate documentation for you. "On using JSON-LD to create evolvable RESTful services"; "Creating 3rd Generation Web APIs with Hydra";"Model Your Application Domain,Not Your JSON Structures". https://www.youtube.com/watch?v=fJCtaNRxg9M; Check also http://www.slideshare.net/lanthaler/building-next-generation-web-ap-is-with-jsonld-and-hydra. Alternatively chech ALPS / Siren.

 - Have further look to the possibilities of NARWHL. http://www.narwhl.com/ to design the API.
 - Offer students of documenting using the classical approach (GET, PUT, POST, DELETE) or the Hypermeida approach (http://stackoverflow.com/questions/24079375/how-to-document-an-api-and-still-respect-hateoas)


 ## THEORY
 - Why to use hypermedia. Interesting discussion in the API craft forum :  https://groups.google.com/forum/#!topic/api-craft/ZxnLD6q6w7w/discussion
 - Study if we can add something out of this: http://slides.com/jcassee/hypermedia-ilt-2015#/4/4



 # LECTURES
 ## Course introduction 

 ### Lecture 1 
 - Find video what is the web? How the WWW works?
 - Include this in the theory: 
		"When greeted by a media type it doesn’t recognize—application/x-shockwave-flash, for example, which is used when an Adobe Flash object is being sent—most browsers have a facility to search for and install a plugin that can handle that media type inline with the rest of what it’s displaying. This makes the browser highly adaptable as new media types representing different technologies arise. So long as a plug-in has been created for the browser and the browser can find it, it will adjust. This adaptability is what has made the web a dominant standard over the last 20 years. It’s not the browsers, but their ability to use the hypermedia facilities used by servers to be able to adjust as new data types become available.  " -> http://www.mashery.com/blog/stop-talking-about-hypermedia-and-rest-start-building-adaptable-apis
 - Compare REST with other APIs. Why REST is better?
 - Check http://jeffknupp.com/blog/2014/06/03/why-i-hate-hateoas/ comments. Advantages of using HATEOAS
 - Why restful APIs. Find real cases RESTful APIs. Compare with SOAP.

 ### Lecture 2
 - Recheck the hypermedia. Hypermedia controls are repeated all around the slides. I have repeated during the lecture at least 10 times all about workflow and suggesting possible next steps. 
 - Add the recommendations on:  http://soabits.blogspot.no/2013/05/error-handling-considerations-and-best.html to describe error messages. 
 - Use paypal api as an example of hateoas
 - Compare hypermedia driven vs classical RESTful
	- Add this clarification to hypermedia"there's nothing wrong with readable URIs and with users being able to easily explore your API by building URIs by hand. As long as they are not using that to drive the actual API usage, that's not a problem at all, and even encouraged by Roy Fielding himsel"
 - Remark: Independent evolvability between server and client: AVOID VERSIONING. Try to provide examples.
 - Reduce the slides and provide more examples. 
 
 ## EXERCISES
 ### Project Work Presentation 
 - Check the slides order. Sometimes there is no flow in the presentation
 - Check that Web Services term has been totally removed, and used Web API instead. 
 - Clarify this is not a website.
 - Provide examples from previous students.

 ### Exercise 0 

 ### Exercise 1 
 - Check if version 1 of Flask is stable.
 - Check how to avoid the Primary Key error that appears if you do not implement correctly some of the methods. It is produced because there is an exception in the original code that does not close the connection, hence it does not execute the teardown correctly (connection is open), data is not deleted from database and then when trying to create something onstart returns the error. One solution would be a try catch onstart if found error try to remove the database/ table structure and then execute it again.
 - REMOVE THE AUTOINCREMENT OR CLARIFY IT. IT IS NOT USED TOTALLY CORRECT in the exercise.
 - Create a method to check current connection. Utilize this method in exercise2 to check that connection has been succesfully closed.
 - Make tests for created table
 
 ### Exercise 2 **
  - If version 1 of Flask is stable -> Do the following: Use the command line to init the database values. (http://flask.pocoo.org/docs/dev/cli/)
  - Consider which is the best form of reporting errors: http://soabits.blogspot.no/2013/05/error-handling-considerations-and-best.html
  - Change the naming. Resources public and private profile might lead to errors when defining the profile.


 ### Exercise 3 
  - Check in API blueprint if affordances and machine state are working
  - Change the naming. Resources public and private profile might lead to errors when defining the profile. 
  - add Test for abort
  - Change documentation message_profile -> message-profile
  - Substitute: 
      > Semantic descriptors used in template: address, avatar, birthday,
           
 the birthday should be birthDate

 ### Exercise 4 
  - Change the structure of the client. It should have one function per link relation. The link relation should be executed on the target (href). 
  - Write tests for jquery and for ui (jasmine??).
  - /admin redirect to /admin/ui.html
  - Validation of mandatory fields. Check if it bootstrap validation is required.
  - Check messages.

 ## PROJECT WORK ASSIGNMENT AND LAYOUT
  
  
 # EVALUATION

 - In API design: Find somekind of syntact evaluator for mason/hal ...





*****ADMINISTRATION*****
