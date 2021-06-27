import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { Buffer } from "buffer";

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor(private http:HttpClient, private router:Router) { }

  login(username: string, password: string){
    this.http.post("http://localhost:5000/login", { username: username, password: password }, {observe: 'response'})
      .subscribe(response => {
        if (response.status === 200){
          this.setSession(response.body);
          this.router.navigate(["/home"]);
        }
      });
  }

  setSession(authResult){
    localStorage.setItem('crs_app_auth_token', authResult.access_token);
  }

  logout() {
    localStorage.removeItem("crs_app_auth_token");
    if (this.router.url !== "/login") {
      this.router.navigateByUrl("/login");
    }
  }

  public getAuthToken(): string {
    return localStorage.getItem("crs_app_auth_token");
  }

  getDecodedToken(): any {
    let base64Url = this.getAuthToken().split('.')[1];
    let base64 = base64Url.replace('-', '+').replace('_', '/');
    return JSON.parse(Buffer.from(base64, 'base64').toString('binary'));
  }

  public isLoggedIn(): boolean {

    let decodedToken = this.getDecodedToken();

    if (!decodedToken) return false;

    let timestampNowSeconds = new Date().getTime() / 1000;
    let isTokenExpired = (timestampNowSeconds - decodedToken.exp > 0);

    return !isTokenExpired;
  }
}
