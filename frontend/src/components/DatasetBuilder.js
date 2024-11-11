import React, { Component } from 'react';
import { saveAs } from 'file-saver';

export default class DataSetBuilder extends Component {
    constructor(props) {
        super(props);
        this.state = {
            EquationSetting: false,
            Equations: [],
            SelectedSets: new Array (false, false, false, false, false, false),  
            Verified: false,
        };
    }

    ChangeEquationSetting = (event) => { // toggle the equation setting
        this.setState({EquationSetting: event.target.value === "true"});
    }

    SubmitEquation = () => {
        // get the equation from the input
        // add it to the list of equations
        let NewEquation = document.getElementById("Equation").value;
        let CurrentEquations = this.state.Equations;
        CurrentEquations.push(NewEquation);
        this.setState({Equations: CurrentEquations}, () => {console.log(this.state.Equations)});
    }

    AddCharacterSets = (event) => {
        // get the character sets from the checkboxes
        // if they have just been checked then add them to the list of character sets
        // if they have just been unchecked then remove them from the list of character sets
        let CurrentSets = this.state.SelectedSets;
        console.log(event.target.value)
        if (CurrentSets[event.target.value] === false) {
            CurrentSets[event.target.value] = true;
        } else {
            CurrentSets[event.target.value] = false;
        }
        this.setState({SelectedSets: CurrentSets}, () => {console.log(this.state.SelectedSets)});


    }
    downloadCSV2D(array) {
        // convert the 2D array to a csv file
        const rows = array.map(row => row.join(','));
        const csv = rows.join('\n');
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
        // save the csv file to the users computer
        saveAs(blob, 'X_train.csv');
      }
    downloadCSV1D(array) {
        // do the same but for a 1D array
        const csv = array.join(',');
        const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
        saveAs(blob, 'Y_train.csv');
        }


    SubmitToAPI = () => {

        console.log(this.state.Verified)
        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json"},
            body: JSON.stringify({
                EquationsBool: this.state.EquationSetting,
                Equations: this.state.Equations,
                Types: this.state.SelectedSets,
                Verified: this.state.Verified,
            }),
        };
        fetch("/api/BuildDataset", requestOptions)
        .then((response) => response.json())
        .then((data) => {
            console.log(data);
            this.downloadCSV2D(data["X_train"]);
            this.downloadCSV1D(data["Y_train"]);
        });
    }



    render() {
        return (
            <div className ="center" style={{display:"flex", flexDirection:"column", alignItems:"center", float:"left", width: "512px", height:"700px", boxShadow:"1px 6px 10px 1px rgba(0,0,0,0.2)", borderRadius:"20px", padding:"10px", justifyContent:"space-around"}}>
                <div>
                    <input type="checkbox" id="verified" name="verified" value={this.state.Verified} checked={this.state.Verified} onChange={() => {this.setState({Verified: !this.state.Verified})}}/>
                    <label style={{paddingLeft: "10px"}} for="verified">Verified</label><br />
                </div>
                {/* have a radio button for if the dataset is for equations or characters */}
                
                <div>
                    <input type="radio" id="equation" name="dataset"  checked={this.state.EquationSetting} value={true} onChange={this.ChangeEquationSetting}/>
                    <label for="equation">Equation</label><br />
                    {/* make this the default */}
                    <input type="radio" id="character" name="dataset" checked={!this.state.EquationSetting} value={false} onChange={this.ChangeEquationSetting}/>
                    <label for="character">Character</label><br />
                </div>
                {/* if the dataset is for equations then show the jsx for the equation version */}
                {this.state.EquationSetting ? (
                    <div style={{display:"flex", flexDirection:"column", alignItems:"center"}}>
                        {/* display the equations that have been added */}
                        <div style={{display:"flex", padding:"5px", overflowY:"scroll", height:"200px", width:"500px", alignItems:"center", justifyContent:"center"}}>
                            {this.state.Equations.map((equation) => (
                                <div>
                                    {equation}
                                </div>
                            ))}
                        </div>

                        <input style={{margin:"2px", borderRadius:"5px", border:"#6f6f6f 1px", borderStyle:"solid", width:"200px"}} type="text" id= "Equation" placeholder="Equation"/>

                        <button style={{marginTop:"10px", width:"200px"}} className="Submit" onClick={this.SubmitEquation}>Submit</button>
                    </div>
                ) : ( 
                    <div>
                        {/* have check boxes for character sets: number, A-J, K-T, U-V, Greek, Operators */}
                        <input type="checkbox" id="number" name="character" value={0} checked={this.state.SelectedSets[0]} onChange={this.AddCharacterSets}/>
                        <label style={{paddingLeft: "10px"}} for="number">Number</label><br />
                        <input type="checkbox" id="A-J" name="character" value={1} checked={this.state.SelectedSets[1]} onChange={this.AddCharacterSets}/>
                        <label style={{paddingLeft: "10px"}} for="A-J">A-J</label><br />
                        <input type="checkbox" id="K-T" name="character" value={2} checked={this.state.SelectedSets[2]} onChange={this.AddCharacterSets}/>
                        <label style={{paddingLeft: "10px"}} for="K-T">K-T</label><br />
                        <input type="checkbox" id="U-V" name="character" value={3} checked={this.state.SelectedSets[3]} onChange={this.AddCharacterSets}/>
                        <label style={{paddingLeft: "10px"}} for="U-V">U-V</label><br />
                        <input type="checkbox" id="Greek" name="character" value={4} checked={this.state.SelectedSets[4]} onChange={this.AddCharacterSets}/>
                        <label style={{paddingLeft: "10px"}} for="Greek">Greek</label><br />
                        <input type="checkbox" id="Operators" name="character" value={5} checked={this.state.SelectedSets[5]} onChange={this.AddCharacterSets}/>
                        <label style={{paddingLeft: "10px"}} for="Operators">Operators</label>
                    </div>
                )
                
                }
                <button className="Submit" onClick={this.SubmitToAPI}>Submit</button>
            </div>
        )
    }
}