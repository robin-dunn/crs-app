import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {

  username: string;
  password: string;

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
  }

  onLoginSubmit(event){
    event.preventDefault();
    this.http.post("http://localhost:5000/login", { username: this.username, password: this.password })
      .subscribe(response => {
        alert(response);
      });
  }

}
