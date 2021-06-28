import { HttpClient } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {

  BASE_URL: string = "http://localhost:5000/";
  tabSelectedIndex: number = 0;
  selectedFile: File;
  projections: string[];
  targetProjection: string;

  // Set some default example GeoJson input.
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
    this.http.get(`${this.BASE_URL}/projections`).subscribe(r => {
      this.projections = r as string[];
      this.targetProjection = this.projections[0] || "None";
    });
  }

  onFileChanged(event: Event){
    let input = event.target as HTMLInputElement;

    if (input.files && input.files.length > 0){
      this.selectedFile = input.files[0];
      console.log(this.selectedFile);
    }
  }

  submitReproject(){
    let requestBody = {
      targetProjection: this.targetProjection,
      geojson: JSON.parse(this.geojson)
    };
    this.geojsonReprojected = "";

    if (this.tabSelectedIndex === 0){
      const formData = new FormData();
      formData.append('targetProjection', this.targetProjection);
      formData.append('file', this.selectedFile);
      if(!this.selectedFile){
        alert("Please select a GeoJSON input file.");
      } else {
        this.http.post(`${this.BASE_URL}/vector/reproject/file`, formData).subscribe(r => {
          this.geojsonReprojected = JSON.stringify(r, null, 2);
        });
      }
    } else {
      this.http.post(`${this.BASE_URL}/vector/reproject/json`, requestBody).subscribe(r => {
        this.geojsonReprojected = JSON.stringify(r, null, 2);
      });
    }
  }
}
