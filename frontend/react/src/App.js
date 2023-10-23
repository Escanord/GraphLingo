// import logo from './logo.svg';
import './App.css';
import ChatComponent from './lex-comp/ChatComponent';
import React from 'react';
import ProxyFrame from './proxy-frame/ProxyFrame';


function App() {
  // let packUrl = (plainUrl) => {
  //   let xhr = new XMLHttpRequest();
  //   let proxyUrl = 'https://cwru-chatbot-rpy.herokuapp.com/' + plainUrl;
  //   xhr.open('GET', proxyUrl);
  //   xhr.onreadystatechange = handleUrlPack;
  //   xhr.responseType = 'blob';
  //   xhr.setRequestHeader('Origin', 'localhost:3000');
  //   xhr.send();
  // }
  
  // client instance
  // const lexClient = new LexRuntimeServiceClient({region: "us-east-1"});
  // const input = {};
  let [frameUrl, setFrameUrl] = React.useState("https://case.edu/");
  let [scrollable, setScrollable] = React.useState("yes");

  

  // function handleUrlPack() {
  //   console.warn("Handling url packing");
  //   if (this.readyState === this.DONE) {
  //     if (this.status === 200) {
  //       // this.response is a Blob, because we set responseType above
  //       var data_url = URL.createObjectURL(this.response);
  //       // document.querySelector('#output-frame-id').src = data_url;
  //       setFrameUrl(data_url);
  //     } else {
  //       console.error('fail');
  //     }
  //   }
  // }


  return (
    <div className="app">
      {/* <ProxyFrame
        /> */}
        <iframe id="background" src={frameUrl} title="embedded website" scrolling={scrollable}></iframe>
      {/* <iframe id="background" src={testHtml} title="embedded website"></iframe> */}
      <ChatComponent
          // client = {lexClient}
          iframeDirection={(url) => {setFrameUrl(url)}}
          updateScrolling={(behavior) => {setScrollable(behavior)}}>
      </ChatComponent>
    </div>
  );
}

export default App;
