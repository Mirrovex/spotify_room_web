import React, { Component } from "react";
import { Button, Grid, Typography, 
        TextField, FormHelperText, 
        FormControl, Radio, RadioGroup,
        FormControlLabel, Collapse } from "@material-ui/core";
import { Link } from "react-router-dom";
import { Alert } from "@material-ui/lab";

export default class CreateRoomPage extends Component {
    static defaultProps = {
        votesToSkip: 1,
        guestCanPause: true,
        update: false,
        roomCode: null,
        updateCallback: () => {},
    }

    constructor(props) {
        super(props);
        this.state = {
            guestCanPause: this.props.guestCanPause,
            votesToSkip: this.props.votesToSkip,
            errorMsg: "",
            successMsg: ""
        };

        this.handleVotesChange = this.handleVotesChange.bind(this);
        this.handleGuestCanPauseChange = this.handleGuestCanPauseChange.bind(this);
        this.handleRoomButtonPressed = this.handleRoomButtonPressed.bind(this);
        this.handleUpdateButtonPressed = this.handleUpdateButtonPressed.bind(this);
    }

    handleVotesChange(e) {
        this.setState({
            votesToSkip: e.target.value,
        });
    }

    handleGuestCanPauseChange(e) {
        this.setState({
            guestCanPause: e.target.value === "true" ? true : false,
        });
    }

    handleRoomButtonPressed() {
        const requestOptions = {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                votes_to_skip: this.state.votesToSkip,
                guest_can_pause: this.state.guestCanPause
            }),
        };
        fetch("/api/create-room/", requestOptions)
        .then((response) => response.json())
        .then((data) => this.props.history.push("/room/" + data.code));
    }

    handleUpdateButtonPressed() {
        const requestOptions = {
            method: "PATCH",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                guest_can_pause: this.state.guestCanPause,
                votes_to_skip: this.state.votesToSkip,
                code: this.props.roomCode
            }),
        };
        fetch("/api/update-room/", requestOptions)
        .then((response) => {
            console.log(response)
            if (response.ok) {
                this.setState({
                    successMsg: "Room updated successfully"
                });
            } else {
                this.setState({
                    errorMsg: "Error updating room"
                });
            }
            this.props.updateCallback();
        });
    }

    renderCreateButtons() {
        return (
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
                    <Button variant="" color="secondary" 
                        to="/" component={Link}>
                        Back
                    </Button>
                    <Button variant="" color="primary"
                        onClick={this.handleRoomButtonPressed}>
                        Create A Room
                    </Button>
                </Grid>
            </Grid>
        );
    }

    renderUpdateButtons() {
        return (
            <Grid item xs={12} align="center">
                <Button variant="contained" color="primary"
                    onClick={this.handleUpdateButtonPressed}>
                    Update Room
                </Button>
            </Grid>
        );
    }

    render() {
        const title = this.props.update ? "Update Room" : "Create Room";

        return (
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
                    <Collapse in={this.state.errorMsg != "" ||
                        this.state.successMsg != ""}>
                        {this.state.successMsg != "" ?
                            (<Alert severity="success"
                                onClose={() => {this.setState({successMsg: ""})}}>
                                {this.state.successMsg}</Alert>) :
                            (<Alert severity="error"
                                onClose={() => {this.setState({errorMsg: ""})}}>
                                {this.state.errorMsg}</Alert>)}
                    </Collapse>
                </Grid>
                <Grid item xs={12} align="center">
                    <Typography component="h4" variant="h4">
                        {title}
                    </Typography>
                </Grid>
                <Grid item xs={12} align="center">
                    <FormControl component="fieldset">
                        <FormHelperText>
                            <div align="center">
                                Guest Control of Playback State
                            </div>
                        </FormHelperText>
                        <RadioGroup row defaultValue={this.props.guestCanPause.toString()}
                            onChange={this.handleGuestCanPauseChange}>
                            <FormControlLabel value="true" 
                                control={<Radio color="primary" />} 
                                label="Play/Pause"
                                labelPlacement="bottom"
                            />
                            <FormControlLabel value="false" 
                                control={<Radio color="secondary" />} 
                                label="No Control"
                                labelPlacement="bottom"
                            />
                        </RadioGroup>
                    </FormControl>
                </Grid>
                <Grid item xs={12} align="center">
                    <FormControl>
                        <TextField required={true} type="number" 
                            value={this.state.votesToSkip}
                            inputProps={{
                                min: 1,
                                style: {textAlign: "center"},
                            }}
                            onChange={this.handleVotesChange}
                        />
                        <FormHelperText>
                            <div align="center">Votes Required To Skip Song</div>
                        </FormHelperText>
                    </FormControl>
                </Grid>
                {this.props.update ? this.renderUpdateButtons() : this.renderCreateButtons()}
            </Grid>
        );
    }
}