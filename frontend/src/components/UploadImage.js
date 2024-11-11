import React, { Component } from "react";
import {
  Card,
} from "@material-ui/core";
import CardMedia from '@mui/material/CardMedia';
import CardContent from '@mui/material/CardContent';
import DownloadIcon from '@mui/icons-material/Download';
import Selector from './SelectorPage';

export default class UploadImage extends Component {
  constructor(props) {
    super(props);
    this.state = { // this is all the data required for the component to function
      FilePreview: "static/images/UploadImagePlaceHolder.jpg",
      NewImage: "", // this is the URL for the processed image
      IMap : "", // this is the image map that is returned from the backend
      Data : null, // this is the processed image that is returned from the backend
      Select : false,
    };
  }

  onFileChange = event => {
    var reader = new FileReader(); // this is the reader that will convert the image to a base64 string
    reader.addEventListener("loadend", () => { this.setState({ FilePreview: reader.result});
     }); // set the state so that the preview image is updated
    reader.readAsDataURL(event.target.files[0]) // convert to base64 string, as that is what the backend expects and is easier to handle
    
  };

  getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();

        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  Submit = event =>
  {
    const CRSFToken = this.getCookie("csrftoken"); // get the CRSF token from the cookie used to validate the request
    const requestOptions = {
      method: "POST", // this is a post request, the request will be directed to a post function at the endpoint specified in the fetch
      headers: { "Content-Type": "application/json", "X-CRSFToken": CRSFToken}, // add the CRSF token to the header
      body: JSON.stringify({
        Image: this.state.FilePreview, //  the base64 string of the image is added to the request data
      }),};
    fetch("/api/UploadHandler", requestOptions) // send the request to api/UploadHandler, see API.py for the endpoint
    .then((response) => response.json()) // format the response to json
    .then((data) => {
      // update the state with the data returned from the backend
      this.setState({Data: data["Blended"]})
      this.setState({IMap: data["Map"]})
      this.setState({NewImage: data["URL"]})
    })
    .then(() =>{ // using a .then here to ensure that the state is updated before the component is rerendered as setState is async
      this.setState({Select : true}) // set the state to true so that the component will rerender and display the selector page
    })    
  }

  render() {
    if (this.state.Select) { // react allows for conditional rendering, this is used to display the selector page if the state is true. I have decided to do this as it means that the user can only go in one direction and can't skip pages, there are other ways to do this but this is the simplest
      return <Selector Data = {this.state.Data} Map = {this.state.IMap} Url = {this.state.NewImage}></Selector> // pass the data to the selector page props
    }
    return (
      <div  className="center">
        <Card style={{padding: "5%", width: "100%"}}> {/* this is the card that will make up the base of the UI, it is a pre-made component that i tweak to fit my requirements  */}
          <div style={{borderRadius:10}}>
            <CardMedia // this is the image preview, it makes use of the material UI component
              overflow="hidden"
              component="img"
              maxHeight="200"
              maxWidth="200"
              image={this.state.FilePreview}
              alt="Image Preview"
              />
          </div>

          <CardContent style={{display: "flex", alignItems: "center", flexDirection: "column"}}> 
            <label htmlFor="fileUpload" className="FileUploadMain" style={{marginRight: "4px", borderRadius: 10, display: "flex", alignItems: "center", justifyContent: "space-evenly",}}> {/* this is the label for the file upload, the css is not from a class as it is not repeated much so it is easy for development to do it here */}
              <DownloadIcon style={{width :"22%"}}></DownloadIcon> {/* this is the icon that is displayed on the button, it is a recognisable icon */}
                Upload Equation
            </label>
            <input type="file" id="fileUpload" accept="image/*" className="FileUpload" onChange={this.onFileChange}></input>  {/* this is the input for the files, the accept attribute ensures only images are uploaded, the css comes from Style.css*/}
            <button className="Submit" onClick={this.Submit}>Submit</button> {/* this is the submit button, it is a simple button that calls the submit function when clicked */}
          </CardContent>
        </Card>
      </div>
    )
  }
}