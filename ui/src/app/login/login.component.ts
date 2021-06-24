import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import * as moment from 'moment';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {

  username: string;
  password: string;

  constructor(private http: HttpClient, private router: Router) { }

  ngOnInit(): void {
  }

  onLoginSubmit(event){
    event.preventDefault();
    this.http.post("http://localhost:5000/login", { username: this.username, password: this.password }, {observe: 'response'})
      .subscribe(response => {
        if (response.status === 200){
          this.setSession(response.body);
          this.router.navigate(["/home"]);
        }
      });
  }

  setSession(authResult){
    const expiresAt = moment().add(authResult.expiresIn,'second');
    localStorage.setItem('crs_app_auth_token', authResult.access_token);
    localStorage.setItem("crs_app_auth_token_expires_at", JSON.stringify(expiresAt.valueOf()));
  }

    logout() {
        localStorage.removeItem("crs_app_auth_token");
        localStorage.removeItem("crs_app_auth_token_expires_at");
    }

    public isLoggedIn() {
        return moment().isBefore(this.getExpiration());
    }

    isLoggedOut() {
        return !this.isLoggedIn();
    }

    getExpiration() {
        const expiration = localStorage.getItem("crs_app_auth_token_expires_at");
        const expiresAt = JSON.parse(expiration);
        return moment(expiresAt);
    }
}
