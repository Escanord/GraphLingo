//imports
import './UrlList.css'

//react
import React from 'react';

//master export
export default function UrlList(props) {
  /*
  urls structure:
  
  SAMPLE RESPONSE TO RECEIVE
  PRIMARILY CARE ABOUT 'response', which is what
  {
    type: 'msg',
    message: 'There are a few options remaining:',  
    data: [{
      type: "url_list",
      from_s3: false,
      data: {
        display: "unordered",
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
    }]
  }


  */

  const types = {
    "ordered": (jsx) => 
      <ol className='url-list'>
        {jsx}
      </ol>,
    "unordered": (jsx) =>
      <ul className='url-list'>
        {jsx}
      </ul>,
    "unbulleted": (jsx) =>
      <p>
        {jsx}
      </p>,
  }
  
  const list_info = props.info;

  // Allows for us to re-direct the Iframe but still have a "link"
  function interceptUrl(url, e){
    e.preventDefault();
    props.iframeDirection(url);
  }

  //return master object
  return types[list_info["display"]](
    list_info["urls"].map( (url_item, index) => {
      console.warn(url_item);
      return (<li
        key = {index}>
          <span
            className='lex-url' 
            onClick={(event) => {interceptUrl(url_item["url"], event)}}>
            <a className='lex-url' href={url_item['url']}>{url_item["text"]}</a>
          </span>
      </li>)
    })
  )
}