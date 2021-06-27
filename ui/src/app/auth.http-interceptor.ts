import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpEvent, HttpResponse, HttpRequest, HttpHandler } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable()
export class AuthHttpInterceptor implements HttpInterceptor {
  constructor(private authService: AuthService){
  }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {

    if (!this.authService.isLoggedIn()) {
      this.authService.logout();
    } else {
      const cloned = req.clone({ headers: req.headers.set("Authorization", "Bearer " + this.authService.getAuthToken()) });
      return next.handle(cloned);
    }

    return next.handle(req);
  }
}
