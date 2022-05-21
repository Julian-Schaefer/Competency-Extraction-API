var spec = {
    "swagger": "2.0",
    "info": {
      "description": "This is our AWT project server. You can query competencies and courses here.",
      "version": "1.0.0",
      "title": "Competency Extraction",
      "license": {
        "name": "Apache 2.0",
        "url": "http://www.apache.org/licenses/LICENSE-2.0.html"
      }
    },
    "tags": [
      {
        "name": "competency",
        "description": "Add and query competencies",
        "externalDocs": {
          "description": "EU ESCO",
          "url": "https://esco.ec.europa.eu/en/classification/skill?uri=http%3A%2F%2Fdata.europa.eu%2Fesco%2Fskill%2FA1.1.0"
        }
      },
      {
        "name": "course",
        "description": "Add and query courses"
      }
    ],
    "schemes": [
      "https",
      "http"
    ],
    "paths": {
      "/competency/{competencyName}": {
        "post": {
          "tags": [
            "competency"
          ],
          "summary": "Add a new competency",
          "description": "",
          "operationId": "addCompetency",
          "consumes": [
            "application/json"
          ],
          "produces": [
            "application/json"
          ],
          "parameters": [
            {
              "in": "path",
              "name": "competencyName",
              "description": "Name of competency to be added",
              "required": true,
              "type": "string"
            },
            {
              "in": "body",
              "name": "competency body",
              "description": "Text of the competency",
              "required": true,
              "schema": {
                "type": "string"
              }
            }
          ],
          "responses": {
            "200": {
              "description": "Competency was added successfully.",
              "schema": {
                "type": "string"
              }
            },
            "400": {
              "description": "Invalid input"
            }
          }
        }
      },
      "/course/{courseName}": {
        "post": {
          "tags": [
            "course"
          ],
          "summary": "Add a new course",
          "description": "",
          "operationId": "addCourse",
          "consumes": [
            "application/json"
          ],
          "produces": [
            "application/json"
          ],
          "parameters": [
            {
              "in": "path",
              "name": "courseName",
              "description": "Name of course to be added",
              "required": true,
              "type": "string"
            },
            {
              "in": "body",
              "name": "course body",
              "description": "Text of the course",
              "required": true,
              "schema": {
                "type": "string"
              }
            }
          ],
          "responses": {
            "200": {
              "description": "Course was added successfully.",
              "schema": {
                "type": "string"
              }
            },
            "400": {
              "description": "Invalid input"
            }
          }
        }
      }
    }
  }