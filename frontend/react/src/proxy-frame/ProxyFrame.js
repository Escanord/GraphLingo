import './ProxyFrame.css';

import React, { Component } from 'react';

export default class ProxyFrame extends Component{
  constructor(props){
    super();

    this.state = {
      frameUrl: 'https://cwru-chatbot-rpy.herokuapp.com/' + "https://case.edu/diversity/",
      scrollable: "yes"
    }
  }

  packUrl = (plainUrl) => {
    let xhr = new XMLHttpRequest();
    let proxyUrl = 'https://cwru-chatbot-rpy.herokuapp.com/' + plainUrl;
    xhr.open('GET', proxyUrl);
    xhr.onreadystatechange = this.handleUrlPack;
    xhr.responseType = 'blob';
    xhr.setRequestHeader('Origin', 'localhost:3000');
    xhr.send();
  }

  handleUrlPack = (response) => {
    console.warn(response);
    console.warn("Handling url packing");
    if (response.target.status === 200) {
      // this.response is a Blob, because we set responseType above
      var data_url = URL.createObjectURL(response.target.response);
      // document.querySelector('#output-frame-id').src = data_url;
      this.setState({frameUrl: data_url});
    } else {
      console.error('fail');
    }
  }

  render(){
    return (
      <iframe id="background" src={this.state.frameUrl} title="embedded website" scrolling={this.state.scrollable}></iframe>
    );
  }
}