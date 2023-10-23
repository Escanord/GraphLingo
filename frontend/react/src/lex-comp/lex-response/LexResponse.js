//imports
import './LexResponse.css';
import UrlList from './UrlList/UrlList';
import RandomResponse from './RandomResponse/RandomResponse';
import CourseClarification from './CourseClarification/CourseClarification';
import InputForm from './InputForm/InputForm';

//react
import React from 'react';
import { ResponseCard } from './response-card/ResponseCard';

//master export
export default function ResponsiveDialog(props) {
  const response = props.response;
  // In case we want to expand this capabilities
  let allowedMsgTypes = {
    "msg": (message) => {
      return <p>{message}</p>
    },
    // "html": (message) => {

    // }
  }

  // Catalogue for all possible data items
  let allowedDataTypes = {
    "message": (index, data) => (
      <p key = {index}>{data['data']['text']}</p>),
    "url_list": (index, data) => (
      <UrlList
        key = {index}
        info={data['data']}
        iframeDirection = {props.iframeDirection}/>),
    "random_response": (index, data) => (
      <RandomResponse
        key = {index}
        responses={data['data']}
        iframeDirection = {props.iframeDirection}/>),
    "course_clarification": (index, data) => (
      <CourseClarification
        key = {index} 
        courses={data['data']}
        responseCallback={props.responseCallback}/>),
    "input_form": (index, data) => (
      <InputForm
        key = {index} 
        form={data['data']}
        responseCallback={props.responseCallback}/>)
  }

  return (<>
    <div className={(props['incomingResponse'] ? "incoming-response" : "user-response") + " response"}>
      {/* Process the message types */}
      {response.message ? 
        allowedMsgTypes[response.type](response.message) : null}

      {/* In case of response cards */}
      {response.card ? 
        <ResponseCard
          responded={props.responseCallback}
          card={response.card}/>: null}

      {/* If there is any kind of bundled data */}
      {response.data ? response.data.map((data, index) => 
        allowedDataTypes[data['type']](index, data)
      ) : null}
    </div>
    </>)
}