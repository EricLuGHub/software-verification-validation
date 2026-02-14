const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");
const testConstants = require("../../testConstants.js");

const host = testConstants.host;
const projectsEndpoint = testConstants.projectsEndpoint;
const projTodoRelationship = testConstants.projTodoRelationship;
const validID = 1;
const invalidID = 20;

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/projects/:id/tasks & /projects/:id/tasks/:id endpoint API Calls - XML", function () {
  beforeEach(async function () {
    child_process.spawn("java", ["-jar", "runTodoManagerRestAPI-1.5.5.jar"]);

    let serverReady = false;
    while (!serverReady) {
      try {
        await chai.request(host).get(projectsEndpoint);
        serverReady = true;
      } catch (err) {}
    }
  });

  //Creating a new task to test project-task relationship
  beforeEach(async () => {
    let body = {
      title: "Gardening",
      doneStatus: false,
      description: "water the plants",
    };
    try {
      await chai.request(host).post("/todos").send(body);
    } catch (err) {}
  });

  afterEach(async function () {
    try {
      await chai.request(host).get("/shutdown");
    } catch (err) {}
  });

  it("HEAD /projects/:id/tasks - Return headers for the todo items related to project, with existing given id - Capability", async function () {
    const response = await chai
      .request(host)
      .head(`${projectsEndpoint}/${validID}/${projTodoRelationship}`)
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);
  });

  it("HEAD /projects/:id/tasks - Return headers for the todo items related to non-existing project,- BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 200
    const response = await chai
      .request(host)
      .head(`${projectsEndpoint}/${invalidID}/${projTodoRelationship}`)
      .set("Content-Type", "application/xml");
    //Actual Expected status is 404
    expect(response).to.have.status(200);
  });

  it("POST /projects/:id/tasks - Create relationship between specified existing project and existing todo instance - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN STATUS CODE 201 AND CREATE RELATIONSHIP ENTITY BIDIRECTIONALLY
    // ACTUAL BEHAVIOR: RETURN ERROR CODE 404 AND ERROR TEXT MESSAGE DUE TO INABILITY TO READ XML
    const body = `<id>2</id>`;
    const response = await chai
      .request(host)
      .post(`${projectsEndpoint}/${validID}/${projTodoRelationship}`)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected =
      '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}';
    expect(response).to.have.status(400);
    expect(response.text).to.deep.equal(expected);
  });

  it("POST /projects/:id/tasks - Create relationship between specified non-existing project and existing todo instance - BUG", async function () {
    //EXPECTED BEHAVIOR: RETURN ERROR CODE 404 AND ERROR MESSAGE: "Could not find parent thing for relationship projects/20/tasks"
    //ACTUAL BEHAVIOR: RETURN ERROR CODE 400 AND ERROR MESSAGE DUE TO INABILITY TO READ XML
    const body = `<id>2</id>`;
    const response = await chai
      .request(host)
      .post(`${projectsEndpoint}/${invalidID}/${projTodoRelationship}`)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected =
      '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}';
    expect(response).to.have.status(400);
    expect(response.text).to.deep.equal(expected);
  });

  it("DELETE /projects/:id/tasks/:id - Delete existing relationship instance between project and todo - Capability", async function () {
    const todoID = 2;
    const response = await chai
      .request(host)
      .delete(
        `${projectsEndpoint}/${validID}/${projTodoRelationship}/${todoID}`
      )
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);

    // Veryfying deletion through get request
    const relationship = await chai
      .request(host)
      .get(`${projectsEndpoint}/${validID}/${projTodoRelationship}`)
      .set("Content-Type", "application/xml");
    const expected = {
      todos: [
        {
          id: "1",
          title: "scan paperwork",
          doneStatus: "false",
          description: "",
          tasksof: [
            {
              id: "1",
            },
          ],
          categories: [
            {
              id: "1",
            },
          ],
        },
      ],
    };

    expect(relationship).to.have.status(200);
    expect(relationship.body).to.deep.equal(expected);
  });

  it("DELETE /todos/:id/tasks/:id - Delete non-existing relationship instance between project and todo- Error Case", async function () {
    const todoID = 20;
    const response = await chai
      .request(host)
      .delete(
        `${projectsEndpoint}/${validID}/${projTodoRelationship}/${todoID}`
      )
      .set("Content-Type", "application/xml");

    const expected = {
      errorMessages: ["Could not find any instances with projects/1/tasks/20"],
    };
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equal(expected);
  });

  it("DELETE /projects/:id/tasks/:id - Delete existing relationship instance between project and todo - Capability", async function () {
    const todoID = 2;
    const response = await chai
      .request(host)
      .delete(
        `${projectsEndpoint}/${validID}/${projTodoRelationship}/${todoID}`
      )
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);

    // Verifying deletion through get request
    const relationship = await chai
      .request(host)
      .get(`${projectsEndpoint}/${validID}/${projTodoRelationship}`)
      .set("Content-Type", "application/xml");
    const expected = {
      todos: [
        {
          id: "1",
          title: "scan paperwork",
          doneStatus: "false",
          description: "",
          tasksof: [
            {
              id: "1",
            },
          ],
          categories: [
            {
              id: "1",
            },
          ],
        },
      ],
    };

    expect(relationship).to.have.status(200);
    expect(relationship.body).to.deep.equal(expected);

    //Checking if todo=>projects relationship is deleted (bidirectionality)
    const taskProjectRel = await chai
      .request(host)
      .get("/todos/2/tasksof")
      .set("Content-Type", "application/xml");
    const expectedProj = {
      projects: [],
    };

    expect(taskProjectRel).to.have.status(200);
    expect(taskProjectRel.body).to.deep.equalInAnyOrder(expectedProj);
  });
});
