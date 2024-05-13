import React, { Component } from "react";
import { TextField, Button, Grid, Typography } from "@material-ui/core";
import { Link } from "react-router-dom";

export default class JoinRoomPage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            roomCode: "",
            error: "",
        };
        this.handleTextFieldChange = this.handleTextFieldChange.bind(this);
        this.roomButtonPressed = this.roomButtonPressed.bind(this);
    }

    handleTextFieldChange(e) {
        this.setState({
            roomCode: e.target.value
        });
    }

    roomButtonPressed() {
        const requestOptions = {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                code: this.state.roomCode
            }),
        };
        fetch("/api/join-room/", requestOptions)
        .then((response) => {
            if (response.ok) {
                this.props.history.push(`/room/${this.state.roomCode}`);
            } else {
                this.setState({error: "Room not found"});
            }
        }).catch((error) => console.error(error));
    }

    render() {
        return (
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
                    <Typography variant="h4" component="h4">
                        Join a Room
                    </Typography>
                </Grid>
                <Grid item xs={12} align="center">
                    <TextField label="Code"
                        error={this.state.error}
                        placeholder="Enter a Room Code"
                        value={this.state.roomCode}
                        helperText={this.state.error}
                        variant="outlined"
                        onChange={this.handleTextFieldChange}
                    />
                </Grid>
                <Grid item xs={12} align="center">
                    <Button variant="" color="secondary"
                        to="/" component={Link}>
                        Back
                    </Button>
                    <Button variant="" color="primary"
                        onClick={this.roomButtonPressed}>
                        Enter Room
                    </Button>
                </Grid>
            </Grid>
        );
    }
}