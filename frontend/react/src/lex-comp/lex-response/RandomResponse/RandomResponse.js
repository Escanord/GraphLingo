//imports
import './RandomResponse.css'
import UrlList from '../UrlList/UrlList';

//react
import React from 'react';

//master export

//Requires STATEful component to remember "Random" state
export default class RandomResponse extends React.Component {
  
  /*
  urls structure:
  
  SAMPLE RESPONSE TO RECEIVE
  PRIMARILY CARE ABOUT 'data'
  [
    {
      msg: "Response 1",
      url_type: "ordered",
      urls: [
        {
          text: "Case",
          url: "https://case.edu"
        },
        {
          text: "Case Admissions",
          url: "https://case.edu/admissions/undergraduate"
        }
      ]
    },
    {
      msg: "Response 2",
      url_type: "unordered",
      urls: []
    },
    {
      msg: "Response 3",
      url_type: "ordered",
      urls: [
        {
          text: "Google",
          url: "https://google.com"
        },
        {
          text: "Case",
          url: "https://case.edu"
        }
      ]
    }
  ]

  */

  constructor(props){
    super();
    // Create a copy so we don't destroy data.
    const allResponses = props.responses.slice();

    // Select the random response
    const targetIndex = Math.floor(Math.random() * props.responses.length);
    const targetResponse = allResponses.splice(targetIndex,1)[0];

    //Initialize the state with the responses
    this.state = {
      responses: allResponses,
      targetResponse: targetResponse,
      showResponses: false
    }
  }
  
  // Create a copy:
  
  render() {
    return (
    <>
      <div className='main-response'>
        <p>{this.state.targetResponse.msg}</p>
        <UrlList
          info = {{
            display: this.state.targetResponse.url_type,
            urls: this.state.targetResponse.urls
          }}
          iframeDirection = {this.props.iframeDirection}/>
      </div>
      <div className='other-responses'>
        <p><span
          className='cwru-button'
          onClick={() => this.setState({showResponses: !this.state.showResponses})}
          >{`Show me ${this.state.showResponses ? "less" : "more"}:`}</span></p>
        {this.state.showResponses ? 
        <div className='hidden-responses'>
          {this.state.responses.map((response, index) => {
            return (<React.Fragment key = {index} ><p className="individual-response">
              {response['msg']}
              </p>
              <UrlList
                info = {{
                  display: response.url_type,
                  urls: response.urls
                }}
                iframeDirection = {this.props.iframeDirection}/>
              {index < this.state.responses.length - 1 ? <hr/> : null}</React.Fragment>)
          })}
        </div> : null}
      </div>
    </>)
  }
}