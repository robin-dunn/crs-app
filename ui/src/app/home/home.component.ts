import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  projections: string[];
  targetProjection: string;
  geojson: string = JSON.stringify(
  {
    "type": "FeatureCollection",
    "name": "example_vector",
    "crs": {
      "type": "name",
      "properties": {
        "name": "epsg:4326"
      }
    },
    "features": [
      {
        "type": "Feature",
        "properties": {},
        "geometry": {
          "type": "Point",
          "coordinates": [
            -1.7071248,
            52.5043046
          ]
        }
      }
    ]
  }, null, 2);
  geojsonReprojected: string;

  constructor(private http:HttpClient) { }

  ngOnInit(): void {
    this.http.get("http://localhost:5000/projections").subscribe(r => {
      this.projections = r as string[];
      this.targetProjection = this.projections[0] || "None";
    });
  }

  submitReproject(){
    let requestBody = {
      targetProjection: this.targetProjection,
      geojson: JSON.parse(this.geojson)
    };
    this.http.post("http://localhost:5000/vector/reproject", requestBody).subscribe(r => {
      this.geojsonReprojected = JSON.stringify(r, null, 2);
    });
  }
}
