import React, { Component } from "react";
import Display from "./DisplayPage";

export default class Selector extends Component {
  constructor(props) {
    super(props);

    this.state = { // the state allows for easy access and handling of data on a users device
      Image: null,
      MapStr: props.Map, // the map is a 2d array that contains the id of the group at each pixel, but for easy of data transfer it is stored as a string
      DataStr: props.Data, // similar to the map, the data is a 2d array that contains the data for each group
      Data: null, // when the component is loaded the data is converted from a string to a 2d array
      Map: null, // same as the data
      Url: props.Url, // the url of the image, passed from the upload page as a prop
      Selected: [],
      SelectedOldValue: {},
      Selecting: false,
      // the following are the variables that will be passed to the display page
      Equation: "",
      StandardForm: "",
      DisplayEquation: false,
      Descriptions: []
    };
    this.canvasRef = React.createRef(); // this is a reference to the canvas element, this is used to get the context of the canvas the html equivalent would be document.getElementById("canvas")
    this.imageRef = React.createRef();
    this.ContainerRef = React.createRef();
  }

  convertStringTo2dArray = (string) => { // as mentioned the data and map are received as strings, this function converts them to 2d arrays
    var array = string.split(";"); // the data is split by a semicolon into rows
    var finalArray = []; // the final array that will be returned
    for (var i = 0; i < array.length; i++) {
      var temp = array[i].split(","); // each row is split by a comma into pixels
      finalArray.push(temp); // the row is added to the final array
    }
    return finalArray;
  }
  componentDidMount() { // this function is called when the component is first loaded
    this.setState({Data: this.convertStringTo2dArray(this.state.DataStr)}) // the data is converted from a string to a 2d array and stored in the state
    this.setState({Map: this.convertStringTo2dArray(this.state.MapStr)})
    const canvas = this.canvasRef.current; // the canvas is retrieved from the reference
    const ctx = canvas.getContext('2d');
    const img = this.imageRef.current;
    img.onload = () => {

      ctx.drawImage(img, 0, 0) // the image (dictated by the URL) is drawn onto the canvas
    }
  }

  SelectClick = event => {
    // the x and y coordinates of the click adjusted for the offset of the canvas 
    const PosX = event.clientX - this.canvasRef.current.offsetLeft - this.ContainerRef.current.offsetLeft + this.ContainerRef.current.clientWidth / 2; 
    const PosY = event.clientY - this.canvasRef.current.offsetTop - this.ContainerRef.current.offsetTop + this.ContainerRef.current.clientHeight / 2;
    const Tartget = this.state.Map[PosY+1][PosX+1]; // the id of the group that was clicked, ignot the spelling mistake
    var temp = this.state.Selected; // the array of selected groups is retrieved from the state
    if (this.checkifTagetisInSelected(Tartget)) { // the user may click on a group that is already selected to remove it from the selection 
      if (this.state.Selecting) { // if the user was in the process of selecting a group then the selection is cancelled and an alert is displayed
        alert("Select the character set");
        console.log("You need to select a character set first");
      }
      else {
        this.setState({Selecting: true}); // the user is now in the process of selecting a group, change this to block the user from selecting another group and show the character set button array
        var Target = this.Getcoordswheremapisx(Tartget, this.state.Map, "Green"); // the group is highlighted in green in the canvas
        let TargetStruct = {
          [Tartget]: Target, // the dimensions of the group are stored in a dictonary with the id of the group as the key
          Type: "number", // the type of the group is stored, this is used to determine which character set to display this is set to number by default but can be changed by the user
        }
        temp.push(TargetStruct); // the dictonary is added to the array of selected groups
        this.setState({Selected: temp}); // the array of selected groups is stored in the state
      }
      
    }
    else {
      var Color = this.state.Data[PosY][PosX] != 0 ? "white" : "black"; // the color of the group is determined by the data, if the data is 0 then the group is black, else then the group is white
      // in this case the group is removed from the selection and the highlight is removed so the original color is found to be drawn back onto the canvas
      this.Getcoordswheremapisx(Tartget, this.state.Map, Color); // the origional colour is drawn back onto the canvas
      this.setState({Selecting: false}); // the user is may have been in the process of selecting a group, and wants to remove it before the character set is selected
      this.removeSelected(Tartget); // the group is removed from the array of selected groups
    }
  }

  removeSelected = (target) => {
    var temp = this.state.Selected; // the array of selected groups is retrieved from the state
    for (var i = 0; i < temp.length; i++) { // loop through the selected groups
      if (target.toString() in temp[i]) { // if the id of the group is in the dictonary then remove it
        temp.splice(i, 1);
        break; // no need to go further, the loop can be exited
      }
    }
    this.setState({Selected: temp}, ()=>{console.log(this.state.Selected)}); // update the state
  }

  checkifTagetisInSelected = (target) => {
    for (var i = 0; i < this.state.Selected.length; i++) { // loop through the selected groups
      if (target.toString() in this.state.Selected[i]) { // if the id of the group is in the dictonary then return false
        return false;
      }
    }
    return true;
  }


  Getcoordswheremapisx = (x, map, color) => {
    let Left = 400, Right = 0, Top = 400, Bottom = 0; // the dimensions are set to the maximum and minimum values possible as placeholders
    const canvas = this.canvasRef.current; // the canvas is retrieved from the reference to be drawn on
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = color; // the colour is set
    for (var i = 0; i < map.length; i++) {
      for (var j = 0; j < map[i].length; j++) { // loop through the map/image
        if (map[i][j] === x) { // if the id of the group is found then draw a pixel of the colour onto the canvas
          ctx.fillRect(j, i, 1, 1); // add a pixel at the current coordinates
          // the maximum and minimum values of the dimensions are found, to be used to crop the image for the neural network later
          if (Left > j){Left = j;} 
          else if (Right < j){Right = j;}   
          if (Top > i){Top = i;}
          else if (Bottom < i){Bottom = i;}
        }
      }
    }
    let Dimensions = { // create a dictonary of the maximum points
      Left: Left-2,  // the dimensions are adjusted to account for the fact that the image is drawn onto the canvas with a border
      Right: Right,
      Top: Top,
      Botom: Bottom+2,
    }
    return Dimensions; // the dictonary is returned
  }

  SubmitSelectToSelectHandler = () => {
    const requestOptions = {
      method: "POST", 
      headers: { "Content-Type": "application/json" }, // on the previous page the csrf token was added to the header of the request, this is normaly done automatically
      body: JSON.stringify({
        Selected: this.state.Selected, // the array of selected groups is sent to the server
        Map  : this.state.Map, // along with the map as it is not stored on the server
      }),
    };
    fetch("/api/Select", requestOptions) // the request is sent to the server, check the urls.py file to see the url that is used
      .then((response) => response.json())
      .then((data) => {
        // the data is retrieved from the server and the state is updated
        this.setState({Equation: data.Equation}, () => {
          this.setState({StandardForm: data.StandardForm}, () => {
            this.setState({Descriptions: data.Descriptions}, () => { // the states are updated one after the other using callbacks to ensure that the data is updated before the next state is updated
              this.setState({DisplayEquation: true}); // this is most important as the DisplayEquation state is used to determine which page to display, if the other states haven't been set then the DisplayPage props will be undefined 
            })
          })
        })});
      
  }

  SelectCharacterSet = (type) => {
    this.setState({Selecting: false}); // the user has completed the process of selecting a group
    var temp = this.state.Selected; // the array of selected groups is retrieved from the state
    var SelectingItem = temp.pop(); // the last item in the array is removed, this is the group that the user has just selected
    SelectingItem.Type = type; // the type of the group is set
    console.log(SelectingItem);
    //SelectingItem.Value = this.state.SelectedValueOrganic;
    temp.push(SelectingItem); // the group is added back to the array of selected groups
    this.setState({Selected: temp}, () => {console.log(this.state.Selected)}); // the state is updated
  }

  render() {
    if (this.state.DisplayEquation) { // if the DisplayEquation state is true then the DisplayEquation component is returned, i have stated why it is done this way in UploadImage.js
      return (<Display Latex={this.state.Equation} StandardForm = {this.state.StandardForm} Descriptions= {this.state.Descriptions}/>) //pass the props to the DisplayEquation component from the state
    }
    return (
      <div ref={this.ContainerRef} className ="center" style={{display:"flex", flexDirection:"column", alignItems:"center", float:"left", width: this.state.Selecting ? ("600px") : ("412px"), height:this.state.Selecting ? ("600px") : ("500px"), boxShadow:"1px 6px 10px 1px rgba(0,0,0,0.2)", borderRadius:"20px", padding:"10px", justifyContent:"space-around"}}>
        {/* the div is given a reference so that SelectClick can access its offset, some of the styling comes from the Style.css file, but alot is custom to this element, particularly the width that is dependent on the selecting bool using a ? conditional operator */}
        <div style={{boxShadow:"1px 3px 5px 1px rgba(0,0,0,0.2)", borderRadius:"20px", marginBottom:"10px"}}>
          <canvas ref={this.canvasRef} width="400px" height="400px" onClick={this.SelectClick}></canvas> {/* the canvas is given a reference so that it can be drawn on, the width and height are set to the size of the image, to make it interactable, the onClick event is set to the SelectClick function*/}
          <img src={this.state.Url} ref={this.imageRef} style = {{display: "none"}}></img> {/* the image is given a reference so that it can be accessed for the canvas, the display is set to none so that it is not visible */}
        </div>
        {
          this.state.Selecting ? ( // if the user is selecting a group then the buttons are displayed
            <div style={{display:"flex", flexDirection:"row", width:"100%", justifyContent:"space-evenly"}}> {/* the options are displayed in a horizontal button array */}
              <button className="CharacterSet" onClick={e => this.SelectCharacterSet("number")}>0 - 9</button> {/* the buttons are given a class name so that they can be styled in the Style.css file, the onClick event is set to the SelectCharacterSet function, passing the type of the group as a parameter */}
              <button className="CharacterSet" onClick={e => this.SelectCharacterSet("A - J")}>A - J</button>
              <button className="CharacterSet" onClick={e => this.SelectCharacterSet("K - T")}>K - T</button>
              <button className="CharacterSet" onClick={e => this.SelectCharacterSet("U - Z")}>U - Z</button>
              <button className="CharacterSet" onClick={e => this.SelectCharacterSet("Greek")}>Greek</button>
              <button className="CharacterSet" onClick={e => this.SelectCharacterSet("+-x/)")}>+-x/</button>
            </div>
          ) : (
            <div>
            </div>
          )
        }
        {/* <input type = "text" onChange={(event) => this.TestChange(event)}/>*/}
        <button className="Submit" onClick={this.SubmitSelectToSelectHandler}>Submit</button> {/* the submit button is given a class name so that it can be styled in the Style.css file, the onClick event is set to the SubmitSelectToSelectHandler function */}
      </div>
    )
  }
}