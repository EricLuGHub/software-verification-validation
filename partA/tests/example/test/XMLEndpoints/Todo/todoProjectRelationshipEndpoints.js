const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const testConstants = require("../../testConstants.js");
const chaiXml = require("chai-xml");
const convert = require("xml-js");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");

const host = testConstants.host;
const todosEndpoint = testConstants.todosEndpoint;
const projRelationship = testConstants.todoProjRelationship;

chai.use(chaiHttp);
chai.use(chaiXml);
chai.use(deepEqualInAnyOrder);

describe("/todos/:id/tasksof and /todos/:id/tasksof/:id endpoint API Calls - XML", function () {
  beforeEach(async function () {
    child_process.spawn("java", ["-jar", "runTodoManagerRestAPI-1.5.5.jar"]);

    let serverReady = false;
    while (!serverReady) {
      try {
        await chai.request(host).get(todosEndpoint);
        serverReady = true;
      } catch (err) {}
    }
  });

  afterEach(async function () {
    try {
      await chai.request(host).get("/shutdown");
    } catch (err) {}
  });

  it("POST /todos/:id/tasksof - Create relationship between specified existing todo and existing project instance - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN STATUS CODE 201 AND CREATE RELATIONSHIP ENTITY BIDIRECTIONALLY
    // ACTUAL BEHAVIOR: RETURN ERROR CODE 404 AND ERROR TEXT MESSAGE DUE TO INABILITY TO READ XML
    const todoID = 2;
    const body = `<id>1</id>`;
    const response = await chai
      .request(host)
      .post(`${todosEndpoint}/${todoID}/${projRelationship}`)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected =
      '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}';
    expect(response).to.have.status(400);
    expect(response.text).to.deep.equal(expected);
  });

  it("POST /todos/:id/tasksof - Create relationship between specified NON-existing todo and existing project instance - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404 AND ERROR MESSAGE: "Could not find parent thing for relationship todos/40/tasksof"
    // ACTUAL BEHAVIOR: RETURN ERROR CODE 400 AND ERROR MESSAGE DUE TO INABILITY TO READ XML
    const todoID = 3;
    const body = `<id>1</id>`;
    const expected =
      '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}';

    const response = await chai
      .request(host)
      .post(`${todosEndpoint}/${todoID}/${projRelationship}`)
      .set("Content-Type", "application/xml")
      .send(body);
    expect(response).to.have.status(400);
    expect(response.text).to.deep.equal(expected);
  });

  it("DELETE /todos/:id/tasksof/:id - Delete existing relationship instance between todo and project - Capability", async function () {
    const todoID = 2;
    const projID = 1;
    const response = await chai
      .request(host)
      .delete(`${todosEndpoint}/${todoID}/${projRelationship}/${projID}`)
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);

    // VERIFYING DATA CHANGES AS EXPECTED BASED ON API CALL
    const projRelationshipsOfTodo = await chai
      .request(host)
      .get(`${todosEndpoint}/${todoID}/${projRelationship}`)
      .set("Content-Type", "application/xml");
    const expected = {
      projects: [],
    };

    expect(projRelationshipsOfTodo).to.have.status(200);
    expect(projRelationshipsOfTodo.body).to.deep.equal(expected);
  });

  it("DELETE /todos/:id/tasksof/:id - Delete non-existing relationship instance between todo and project (eg after it has already been deleted)- Error Case", async function () {
    const todoID = 2;
    const projID = 1;
    const response = await chai
      .request(host)
      .delete(`${todosEndpoint}/${todoID}/${projRelationship}/${projID}`)
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);

    // VERIFYING DATA CHANGES AS EXPECTED BASED ON API CALL
    const secondAttemptResponse = await chai
      .request(host)
      .delete(`${todosEndpoint}/${todoID}/${projRelationship}/${projID}`)
      .set("Content-Type", "application/xml");
    const expected = {
      errorMessages: [
        `Could not find any instances with todos/${todoID}/tasksof/${projID}`,
      ],
    };
    expect(secondAttemptResponse.body).to.deep.equal(expected);
    expect(secondAttemptResponse).to.have.status(404);
  });
});
