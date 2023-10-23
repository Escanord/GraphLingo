import './ChatComponent.css';
import LexResponse from './lex-response/LexResponse';
import LexExpand from './lex-expand/LexExpand';
import S3Retreival from './s3-service/S3Retreival';

import React, { Component } from 'react';

// Icons:
import { BsChatDotsFill, BsChatFill, BsThreeDots } from "react-icons/bs";
import { IoMdClose, IoIosSend, IoIosArrowUp, IoIosArrowDown, IoIosRefresh } from "react-icons/io";

// LEX SDK V3:
import { LexRuntimeServiceClient, PostTextCommand } from "@aws-sdk/client-lex-runtime-service"
import { CognitoIdentityClient } from "@aws-sdk/client-cognito-identity"
import { fromCognitoIdentityPool } from "@aws-sdk/credential-providers"

// INTERACT.js
import interact from 'interactjs';

const REGION = "us-east-1";
const IDENTITY_POOL_ID = "us-east-1:3695bd7e-ef79-42c3-8cba-bf8f944851c6";
// const SESSION_USER_ID = "cwru-chatbot-" + Date.now();

// https://github.com/aws/aws-sdk-js-v3/issues/2870 FOR clientConfig
const lexClient = new LexRuntimeServiceClient({
  region: REGION,
  credentials: fromCognitoIdentityPool({
    client: new CognitoIdentityClient({region: REGION}),
    clientConfig: {region: REGION},
    identityPoolId: IDENTITY_POOL_ID
  })
});



function lexPostParams(input, userId){
  return {
    botAlias: "cwruChatBot",
    botName: "cwruChatBot",
    inputText: input,
    userId: userId// For example, 'chatbot-demo'.
  }
}

// async function testAsync(){
//   console.log("start");
//   const result = await S3Retreival.jsonFrom("https://cwru-chatbot.s3.amazonaws.com/sample.json");
//   console.log("end", result);
// }

// const data = lexClient.send(new PostTextCommand(lexPostParams("I want to search for a course")));
// console.warn(data);

// Interact.js
// const chatwindow = interact('.chatbot-interaction')
//   .resizable({
//     edges: { top: true, left: true },
//     listeners: {
//       move: function (event) {
//         let { x, y } = event.target.dataset

//         x = (parseFloat(x) || 0) + event.deltaRect.left
//         y = (parseFloat(y) || 0) + event.deltaRect.top

//         Object.assign(event.target.style, {
//           width: `${event.rect.width}px`,
//           height: `${event.rect.height}px`,
//           // transform: `translate(${x}px, ${y}px)`
//         })

//         Object.assign(event.target.dataset, { x, y })
//       }
//     }
//   });

// const lexExpandIjs = interact('.cbi-expansion')
//   .resizable({
//     edges: { left: true },
//     listeners: {
//       move: function (event) {
//         let { x, y } = event.target.dataset

//         x = (parseFloat(x) || 0) + event.deltaRect.left
//         y = (parseFloat(y) || 0) + event.deltaRect.top

//         Object.assign(event.target.style, {
//           width: `${event.rect.width}px`,
//           height: `${event.rect.height}px`,
//           // transform: `translate(${x}px, ${y}px)`
//         })

//         Object.assign(event.target.dataset, { x, y })
//       }
//     }
// });

export default class ChatComponent extends Component{
    constructor(props) {
      super(props);
      // Initial state:
      this.state = {
        open: false,
        userText: "",
        responses:[
          {
            response:{
              type: "msg", 
              message:"How can I help you today?",
              data:null, 
              expansionData:null
            },
            incomingResponse: true
          }
        ],
        userId: "cwru-chatbot-" + Date.now(),
        maximize: false,
        expansionData: null,
        waiting: false
      }

      //References to elements on the page for dynamic updates.
      this.userText = React.createRef();
      this.interactionBody = React.createRef();
      this.ibContainer = React.createRef();
      
      // Parent callbacks for iFrame function controls
      this.iframeDirection = props.iframeDirection;
      this.updateScrolling = props.updateScrolling;

      // Test search results for error handling
      let sampleFetch = async() => {
        await new Promise(resolve => {
          const testUrl = 'https://cse.google.com/cse/element/v1?&num=4&cx=004305171799132815236:ciq4c8b3yv4&q=stuff&cse_tok=AJvRUv1FggNRf1tGTCvIyJVyMRbs:1650950882037&callback=sample';
          fetch(testUrl).then(
            (res) => {
              console.warn(res);
              resolve(res);
            }
          )
        });
      }
      // sampleFetch();

      // Provides a callback to allow other components to send user lex queries
      this.responseCallback = (text, value) => {
        this.addUserQuery(text);    //Text indicates what the user input
        this.sendQueryRequest(value);   //Value is the query value.
      }
    }

    /* === Lifecycle hooks === */
    componentDidMount(){
      // Check reize and update the body directions
      window.addEventListener('resize', ()=>{this.updateBodyDirection()});
    }

    componentWillUnmount(){
      // Check reize and update the body directions
      window.removeEventListener('resize', () => {this.updateBodyDirection()});
    }

    /* === CHAT WINDOW CONTROLS === */
    // Functions that control the chat window display

    // Opens the chat bot
    openChat(){
      this.setState({open:true});   // Open the chat window
      this.scrollChatBottom();      // Scroll to the bottom in case there is already content


      // OVERRIDE TO TEST VARIOUS MESSAGE TYPES:
      // const response1 = {
      //   incomingResponse: true,
      //   response: {
      //     type: 'msg',
      //     message: 'There are a few options remaining:',  
      //     data: [{
      //       type: "url_list",
      //       from_s3: false,
      //       data: {
      //         display: "unordered",
      //         urls: [
      //           {
      //             text: "Google",
      //             url: "https://google.com"
      //           },
      //           {
      //             text: "Case",
      //             url: "https://case.edu"
      //           },
      //           {
      //             text: "Case",
      //             url: "https://case.edu/admissions/undergraduate"
      //           }
      //         ]
      //       }
      //     }]
      //   }
      // }

      // const response2 = {
      //   incomingResponse: true,
      //   response: {
      //     type: 'msg',
      //     message: '',
      //     data: [
      //       {
      //         type: "message",
      //         from_s3: false,
      //         data: {"text": "This is the invariant part."}
      //       },
      //       {
      //         type: "url_list",
      //         from_s3: false,
      //         data: {
      //           display: "unordered",
      //           urls: [
      //             {
      //               text: "Google",
      //               url: "https://google.com"
      //             },
      //             {
      //               text: "Case",
      //               url: "https://case.edu"
      //             },
      //             {
      //               text: "Case",
      //               url: "https://case.edu/admissions/undergraduate"
      //             }
      //           ]
      //         }
      //       },
      //       {
      //       type: "random_response",
      //       from_s3: false,
      //       data: [
      //         {
      //           msg: "Response 1",
      //           url_type: "ordered",
      //           urls: [
      //             {
      //               text: "Case",
      //               url: "https://case.edu"
      //             },
      //             {
      //               text: "Case Admissions",
      //               url: "https://case.edu/admissions/undergraduate"
      //             }
      //           ]
      //         },
      //         {
      //           msg: "Response 2",
      //           url_type: "unordered",
      //           urls: []
      //         },
      //         {
      //           msg: "Response 3",
      //           url_type: "ordered",
      //           urls: [
      //             {
      //               text: "Google",
      //               url: "https://google.com"
      //             },
      //             {
      //               text: "Case",
      //               url: "https://case.edu"
      //             }
      //           ]
      //         }
      //       ]
      //     }]
      //   }
      // }

      // this.pushResponse(response1);
      // this.pushResponse(response2);
      // https://case.edu/search-results/?q=cat&cx=004305171799132815236%253Aciq4c8b3yv4&ie=UTF-8&sa=search
      // admission site:case.edu
    }

    // Close the chat dialog
    closeChat(){
      this.maximize(false);   // Minimize the chatwindow
      this.setState({         // Close the chat window
        open: false
      })
    }

    // Refresh (clear history and start a new session)
    refreshChat(){
      this.setState({
        responses:[
          {
            response:{type: "msg", message:"How can I help you today?",data:null, expansionData:null},
            incomingResponse: true
          }
        ],
        userId: "cwru-chatbot-" + Date.now(),
        maximize: false,
        expansionData: null,
      })
    }

    scrollChatBottom(){
      //Automatically scroll the window to the bottom.
      setTimeout(()=>{
        this.interactionBody.current.scrollTop = this.interactionBody.current.scrollHeight;
      }, 100);
      this.forceUpdate();
    }

    // Expand the chatbot to fullscreen
    maximize (value=undefined){
      this.setState({maximize: value === undefined ? !this.state.maximize : value})
      this.scrollChatBottom();
      
      setTimeout(() => {
        this.updateBodyDirection();
        this.updateScrolling(this.state["maximize"] ? "no" : "yes");
      }, 5);
    }
    // Expads he expansion area with the provided data:
    expand (data){
      //The incoming message requires information to be pushed onto the expansion area.
      if(data && data.length !== 0){
        this.setState({expansionData: []});
        setTimeout(()=>{
          this.setState({expansionData: data});
          this.maximize(true);
        }, 100)
      }
    }

    // Send response when user hits enter key
    sendInput(event){
      if(event.code === "Enter"){
        this.sendQuery();        //Try and query lex
        event.preventDefault(); //Stops the enter from being put into the textarea
      }
    }

    /* === RESPONSIVE MONITORS === */
    // Functions that assist with responsive operations

    //Callback to resize the input textarea to exapand with user input.
    updateSize(event){
      event.target.style.height = "";
      event.target.style.height = event.target.scrollHeight+"px"
    }

    //Sets the flex direction of the full screen lexbot depending on window aspect ratio.
    updateBodyDirection(){
      // console.warn("update", this.ibContainer);
      if(this.ibContainer.current){
        // console.warn(this.ibContainer.current.className)
        let currentClasses = "chatbot-interaction-body";
        currentClasses += this.ibContainer.current.clientHeight > this.ibContainer.current.clientWidth ? " cib-vertical" : " cib-horizontal";
        this.ibContainer.current.className = currentClasses;
        // console.warn(this.ibContainer.current.clientHeight, this.interactionBody.current.clientWidth)
        // this.ibContainer.current.style.flexDirection = this.ibContainer.current.clientHeight > this.ibContainer.current.clientWidth ? 'column' : 'row';
        this.forceUpdate();
      }
    }

    /* === LEX INTERACTIONS === */
    // Functions that control the interactions with lex and how to display them

    // Add the new response into the tracked responses whether its from lex or the user
    pushResponse(response){
      this.state.responses.push(response);
      this.scrollChatBottom();
    }

    // Constructs a user query to be pushed to responses.
    addUserQuery(value){
      this.pushResponse({
        response: {
          type: "msg", 
          message: value
        },
        incomingResponse:false
      });
      this.forceUpdate();
    }

    // Submit a user response
    sendQuery(){
      const userInput = this.userText.current.value;
      // Only perform an action if there is something in the input
      if(userInput){
        this.userText.current.value = "";   // Clear the text input
  
        this.addUserQuery(userInput);       // Track the user query
        this.sendQueryRequest(userInput);   // Query lex
      }
    }

    /**
     * Query the lex backend for a response
     * @param {*} value The string message to be sent to lex.
     */
    async sendQueryRequest(value){
      console.warn(this.state.userId);

      //Add waiting bubble
      this.setState({waiting: true});

      // Post / Get HERE:
      // TODO hit new endpoint:

      // lexClient.send(new PostTextCommand(lexPostParams(value, this.state.userId))).then(
      //   async (data) => {
      //     //Response good
      //     //Create the incoming object:
      //     console.warn(data);
      //     let incomingObj = JSON.parse(data.message);
      //     incomingObj['card'] = data.responseCard;


      //     //Check if any of the resources are from s3:
      //     // console.warn(incomingObj);
      //     // Bad coding but necessary for Synchronous Async?
      //     // BLOCKS until BOTH complete and pull json, so a "from_s3" should never be true.
      //     if(incomingObj['data']){
      //       for (let i = 0; i < incomingObj['data'].length; i++){
      //         const dataObject = incomingObj['data'][i];
      //         if(dataObject['from_s3']){
      //           dataObject['from_s3'] = false;
      //           const s3Object = await S3Retreival.jsonFrom(dataObject['data']);
      //           dataObject['data'] = s3Object;
      //         }
      //       }
      //     }
      //     console.warn("data checked");

      //     if(incomingObj['expansionData']){
      //       for (let i = 0; i < incomingObj['expansionData'].length; i++){
      //         const dataObject = incomingObj['expansionData'][i];
      //         if(dataObject['from_s3']){
      //           dataObject['from_s3'] = false;
      //           const s3Object = await S3Retreival.jsonFrom(dataObject['data']);
      //           dataObject['data'] = s3Object;
      //         }
      //       }
      //     }
      //     console.warn("expansion data checked");

      //     console.warn(incomingObj);
      //     //expansiondata:

      //     //Done waiting for response
      //     this.setState({waiting: false});

      //     //Push a response into the history:
      //     this.pushResponse({
      //       response: incomingObj,
      //       incomingResponse: true
      //     });
          
      //     //Pass info to be expanded if it exists
      //     this.expand(incomingObj.expansionData);
          
      //     //If the intent was completed successfully, clear out all previous values to avoid collisions.
      //     if(data.dialogState === "Fulfilled"){
      //       // Reset userID
      //       // this.setState({
      //       //   userId: "cwru-chatbot-" + Date.now()
      //       // });
      //     }
      //   },
      //   (error) => {
      //     // There was an error calling lex.
      //     console.error("LEX ERROR ENCOUNTERED")
      //     console.error(error);
      //     this.pushResponse({
      //       response: {
      //         type: "msg",
      //         message: "There was an error processing your request. Please try again later."
      //       },
      //       incomingResponse: true
      //     });
      //     this.setState({
      //       userId: "cwru-chatbot-" + Date.now(),
      //       waiting: false,
      //     });
      //   }
      // );
    }


    render() {
        return <>
          <div className={`${"chatbot"} ${this.state.maximize? "cb-maximized" : ""}`}>
            {this.state.open ? 
              // Showing the full chatbot
              <div className={`${"chatbot-interaction"} ${this.state.maximize? "cbi-maximized" : ""}`}>
                {/* HEADER */}
                <div className='chatbot-interaction-header'>
                  {this.state.maximize ? 
                  <IoIosArrowDown
                  className='chatbot-clickable chatbot-icons-large'
                  onClick={()=>{this.maximize()}}/>:
                  <IoIosArrowUp
                    className='chatbot-clickable chatbot-icons-large'
                    onClick={()=>{this.maximize()}}/>}
                  <div className='chatbot-interaction-title'>
                    <span className='title-test'>
                      VACAS
                    </span>
                  </div>
                  <IoIosRefresh 
                      className='chatbot-clickable chatbot-icons-medium'
                      onClick={() => {this.refreshChat()}}/>
                  <IoMdClose
                    className='chatbot-clickable chatbot-icons-large'
                    onClick={()=>{this.closeChat()}}/>
                </div>
                {/* Response displays */}
                <div 
                  className='chatbot-interaction-body'
                  ref={this.ibContainer}
                  >
                  <div 
                    ref={this.interactionBody}
                    className='chatbot-interaction-body-se'>
                    {/* ADD ANY RESPONSES HERE */}
                    {this.state.responses.map((response, index) => 
                      (<LexResponse 
                          key = {index}
                          response = {response.response}
                          incomingResponse = {response.incomingResponse}
                          responseCallback = {this.responseCallback}
                          iframeDirection = {this.iframeDirection}/>)
                    )}
                    {/* Pending chatbot */}
                    {
                      this.state["waiting"] ? 
                      // THIS IS BAD, RELIES ON CLASSES IN DIFFERENT COMPONENT
                      <div className="incoming-response response">
                        <BsThreeDots className='chatbot-icons-medium'/>
                      </div> : null
                    }

                  </div>
                  {
                    this.state.maximize ? <div className='chatbot-interaction-body-se cbi-expansion'>
                    <LexExpand
                      data={this.state.expansionData}/>
                  </div> : null
                  }
                </div>
                {/* User input */}
                <form className='chatbot-interaction-footer'>
                  <textarea 
                    ref={this.userText}
                    itemID='userInput'
                    placeholder='Enter your questions here...'
                    onKeyDown={(e)=>{this.sendInput(e)}}
                    onChange={(e)=>{this.updateSize(e)}}
                    className='chatbot-input'>
                  </textarea>                  
                  <IoIosSend
                    onClick={(e)=>{this.sendQuery();console.log(e)}}
                    className='chatbot-clickable chatbot-icons-large'/>
                </form>
              </div>
              : 
              // Showing the chat bubble
              <div 
                title="Let me know how I can help!"
                className='chat-icon chatbot-clickable' 
                onClick={()=>{this.openChat()}}>
                <BsChatFill className='icon-background' />
                <BsChatDotsFill className='icon-foreground'/>
              </div>
            }
          </div>
        </>
    }
}