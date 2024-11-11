import React, { Component } from 'react';
import {
    Card,
    Typography,
  } from "@material-ui/core";
// load some icons 
import IconButton from '@mui/material/IconButton';
import ThumbDownIcon from '@mui/icons-material/ThumbDown';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import TextField from '@mui/material/TextField';
import { MathComponent } from "mathjax-react"; // this is used to properly render the latex

export default class Display extends Component {

    constructor(props) {
        super(props);
        this.state = {
            // the state is loaded from the props that are passed in
            Latex: props.Latex,
            StandardForm: props.StandardForm,
            Descriptions: props.Descriptions,
            SearchLink: "https://www.google.com/search?q=" + props.StandardForm, // it is easy to create a search link using the standard form of the equation
            Verified: true,
        };
    }

    UpvoteHandler = (id, Direction) => { // this is a function that is called when a user upvotes or downvotes a description

        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json"},
            body: JSON.stringify({ // the backend need the id of the description and whether the user is upvoting or downvoting to update the database
                Id: id,
                UpOrDown: Direction,
            }),
        };
        fetch("/api/VoteDescription", requestOptions) // send the request to the backend, api/urls.py specifies the endpoint
        .then((response) => response.json())
        .then((data) => {
            this.setState({Descriptions: data["Descriptions"]}); // the updated descriptions are returned from the backend and the state is updated
        });
    }
    NewDescHandler = (event) => { // this is a function that is called when a user submits a new description
        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json"},
            body: JSON.stringify({
                Standard: this.state.StandardForm, // the backend needs the standard form of the equation to update the database
                Description: event, // the users description
            }),
        };
        fetch("/api/SubmitDescription", requestOptions) // send the request to the backend, api/urls.py specifies the endpoint
        .then((response) => response.json())
        .then((data) => {
            this.setState({Descriptions: data["Descriptions"]}); // the updated descriptions are returned from the backend and the state is updated
        });
    }

    Verify = () => { // if the user is happy with the equation they can click this button to verify it so the dataset can be confident in the labels
        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json"},
        };
        fetch("/api/VerifyCharacter", requestOptions)  // a simple post request to the backend, no data a the EquationImage id is stored in the session

    }

    render() {
        return (
            <div className ="center" style={{display:"flex", flexDirection:"column", alignItems:"center", float:"left", width: "512px", height:"700px", boxShadow:"1px 6px 10px 1px rgba(0,0,0,0.2)", borderRadius:"20px", padding:"10px", justifyContent:"space-around"}}>
                {/* the base of this component take a large amount of styling from Style.css, the most notable part of the styling is the flex direction that says to format elements vertically */}
                {/* display the equation in all its forms */}
                <p style={{textAlign:"center"}}>The equation for a line is:</p>
                <MathComponent tex={this.state.Latex} /> {/* this is the prebuilt component that renders the latex */}
                <p style={{textAlign:"center"}}>The standard form of the equation is:</p>
                <p style={{textAlign:"center"}}>{this.state.StandardForm}</p>
                <p style={{textAlign:"center"}}>The LaTeX form of the equation is:</p>
                <p style={{textAlign:"center"}}>{this.state.Latex}</p>
                <button className="Submit" onClick={() => this.Verify()}>This is what I wanted</button> {/* this button calls the verify function */}
                <p style={{textAlign:"center"}}>Click <a href={this.state.SearchLink} target="_blank" rel="noopener noreferrer">here</a> to quick search the equation</p> {/* this is a link to a search engine with the standard form of the equation */}
                    <div>
                        <p style={{textAlign:"center"}}>Descriptions:</p>
                        <div style={{overflowY:"scroll", height:"200px", width:"500px"}}> {/* this is a scrollable div that contains all the descriptions */}
                            {this.state.Descriptions.map((item, index) => { // map the descriptions to a card
                                return (
                                    <Card key={index} style={{margin:"10px", padding:"10px", display:"flex", flexDirection:"row"}}>
                                        <div style={{width:"20%", display:"flex", flexDirection:"column", justifyContent:"space-around", alignItems:"center"}}>
                                            {/* the upvote and downvote buttons call the upvote handler with the id of the description and +/- 1 to indicate upvote or downvote */}
                                            <IconButton style={{margin:"10px"}} onClick={() => this.UpvoteHandler(item.Id, 1)}>
                                                <ThumbUpIcon/>
                                            </IconButton>
                                            <Typography style={{margin:"10px"}}>{item.Votes}</Typography> {/* display the number of votes in the middle of up and down arrows */}
                                            <IconButton style={{margin:"10px"}} onClick={() => this.UpvoteHandler(item.Id, -1)}>
                                                <ThumbDownIcon/>
                                            </IconButton>
                                        </div>
                                        <Typography style={{margin:"10px", textAlign:"center"}}>{item.Description}</Typography> {/* display the description */}
                                    </Card>
                                )
                            })}
                            {/* this is a card that allows the user to submit a new description */}
                            <Card style={{margin:"10px", padding:"10px", display:"flex", flexDirection:"column", alignItems:"center",}}>
                                <TextField style={{paddingBottom:"10px"}} fullWidth label="Feel free to write a new description" id="NewDesc"/>
                                <button className="Submit" onClick={() => this.NewDescHandler(document.getElementById("NewDesc").value)}>Submit</button>
                            </Card>
                        </div>
                    </div>
                
          </div>
        );
    }
}
