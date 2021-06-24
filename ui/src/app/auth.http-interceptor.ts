import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpEvent, HttpResponse, HttpRequest, HttpHandler } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class AuthHttpInterceptor implements HttpInterceptor {
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {

    const authToken = localStorage.getItem("crs_app_auth_token");

    if (authToken) {
        const cloned = req.clone({
            headers: req.headers.set("Authorization", "Bearer " + authToken)
        });

        return next.handle(cloned);
    }
    else {
        return next.handle(req);
    }

    return next.handle(req);
  }
}
