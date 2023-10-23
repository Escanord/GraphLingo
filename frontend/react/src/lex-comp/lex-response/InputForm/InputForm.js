//imports
import './InputForm.css'

//react
import React from 'react';

import FormControlLabel from '@mui/material/FormControlLabel'
import FormControl from '@mui/material/FormControl'
import FormLabel from '@mui/material/FormLabel'
import Radio from '@mui/material/Radio';
import { RadioGroup } from '@mui/material';
import Button from '@mui/material/Button';

// Styling:
import { createTheme, ThemeProvider } from '@mui/material/styles';
import { orange } from '@mui/material/colors';

//master export

//Requires STATEful component to remember "Random" state
export default class InputForm extends React.Component {
  
  /*
  urls structure:
  
  SAMPLE RESPONSE TO RECEIVE
  PRIMARILY CARE ABOUT 'data'
  {
    incomingResponse: true,
    response: {
      type: 'msg',
      message: 'Please provide us some information about ___:',
      data: [{
        type: "input_form",
        from_s3: false,
        data: [
          {
            key: "breadth",
            label: "Breadth",
            type: "true_false",
            value: "false",
          },
          {
            key: "workload",
            label: "How would you rate the workload?",
            type: "difficulty",
            value: "ok"
          }
        ]
      }]
    }
  }

  */

  // Set the theme
  formTheme = createTheme({
    palette: {
      mode: 'dark',
      primary: {
        main: '#3168a6'
      },
      text: {
      }
    },
  });

  // Catalogue for all possible expansion items
  types = {
    "true_false": (label, key) => (
      <FormControl>
        <FormLabel id = {key}>{label}</FormLabel>
        <RadioGroup
          row
          value={this.state[key]}
          onChange={(e) => {console.warn(e);this.setState({[key]:e.target.value})}}
          defaultValue='false'>
          <FormControlLabel value = "false" control={<Radio size='small'/>} label="False" labelPlacement='top'></FormControlLabel>  
          <FormControlLabel value = "true" control={<Radio size='small'/>} label="True" labelPlacement='top'></FormControlLabel>  
        </RadioGroup>
      </FormControl>
    ),
    "difficulty": (label, key) => (
      <FormControl>
        <FormLabel id = {key}>{label}</FormLabel>
        <RadioGroup
          row
          value={this.state[key]}
          onChange={(e) => {console.warn(e);this.setState({[key]:e.target.value})}}
          defaultValue='ok'>
          <FormControlLabel value = "low" control={<Radio size='small'/>} label="Too Low" labelPlacement='top'></FormControlLabel>  
          <FormControlLabel value = "ok" control={<Radio size='small'/>} label="Ok" labelPlacement='top'></FormControlLabel>  
          <FormControlLabel value = "high" control={<Radio size='small'/>} label="Too High" labelPlacement='top'></FormControlLabel>  
        </RadioGroup>
      </FormControl>
    ),
  }

  constructor(props){
    super();
    // Create a copy so we don't destroy data.
    const form = props.form;
    console.warn(form);

    const testObj = {

    }

    form.forEach(element => {
      console.warn(element);
      testObj[element['key']] = element['value'];
    });

    console.warn(testObj);
    this.state = testObj;
  }
  
  formObject(event){
    console.warn(event);
    console.warn(this.state);
  }

  submit(event){
    this.props.responseCallback("Response submitted!"/* + JSON.stringify(this.state)*/, JSON.stringify(this.state));
  }

  render() {
    return (
      <ThemeProvider theme={this.formTheme}>
        <form>
          {this.props.form.map((value, index) => {
            // console.warn(value);
            return <div key={index}>
              {this.types[value["type"]](value["label"], value["key"])}
            </div>
          })}
          <Button variant="contained" onClick={(event) => {this.submit(event)}}>Submit</Button>
        </form>
      </ThemeProvider>
    )
  }
}