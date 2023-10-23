import './ResponseCard.css';

//react
import React from 'react';

//master export
export function ResponseCard(props) {
  let [value, setValue] = React.useState("");
  // console.warn(props);

  //return master object
  return (
    <div className='response-buttons'>
      {props.card.genericAttachments[0].buttons.map((button, index) => {
        // Split by comma because of response card limitations
        let [title, tooltip] = button['text'].split(/\s*,\s*/)

        return (
          <button 
            title={tooltip}
            key={index}
            type="button" 
            onClick={() => {props.responded(title,button['value'])}}>
            {title}
          </button>)
      }
        
      )}
    </div>
  )
}