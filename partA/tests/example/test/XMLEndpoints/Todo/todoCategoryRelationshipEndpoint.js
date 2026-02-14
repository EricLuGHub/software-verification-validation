const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const testConstants = require("../../testConstants.js");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");

const host = testConstants.host;
const todosEndpoint = testConstants.todosEndpoint;
const categRelationship = testConstants.categoriesRelationship;

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/todos/:id/categories and /todos/:id/categories/:id endpoint functioning API Calls - JSON", function () {
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

  it("POST /todos/:id/categories - Create relationship between specified existing todo and existing category instance - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN STATUS CODE 201 AND CREATE RELATIONSHIP ENTITY BIDIRECTIONALLY
    // ACTUAL BEHAVIOR: RETURN ERROR CODE 404 AND ERROR TEXT MESSAGE DUE TO INABILITY TO READ XML
    const todoID = 2;
    const body = `<id>2</id>`;
    const response = await chai
      .request(host)
      .post(`${todosEndpoint}/${todoID}/${categRelationship}`)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected =
      '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}';
    expect(response).to.have.status(400);
    expect(response.text).to.deep.equal(expected);
  });

  it("POST /todos/:id/categories - Create relationship between specified NON-existing todo and existing category instance - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404 AND ERROR MESSAGE: "Could not find parent thing for relationship todos/40/categories"
    // ACTUAL BEHAVIOR: RETURN ERROR CODE 400 AND ERROR MESSAGE DUE TO INABILITY TO READ XML
    const todoID = 40;
    const body = `<id>2</id>`;
    const expected =
      '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}';
    const response = await chai
      .request(host)
      .post(`${todosEndpoint}/${todoID}/${categRelationship}`)
      .set("Content-Type", "application/xml")
      .send(body);
    expect(response).to.have.status(400);
    expect(response.text).to.deep.equal(expected);
  });

  it("DELETE /todos/:id/categories/:id - Delete existing relationship instance between todo and category - Capability", async function () {
    const todoID = 1;
    const categID = 1;
    const response = await chai
      .request(host)
      .delete(`${todosEndpoint}/${todoID}/${categRelationship}/${categID}`)
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);

    // VERIFYING DATA CHANGES AS EXPECTED BASED ON API CALL
    const categRelationshipsOfTodo = await chai
      .request(host)
      .get(`${todosEndpoint}/${todoID}/${categRelationship}`)
      .set("Content-Type", "application/xml");
    const expected = {
      categories: [],
    };

    expect(categRelationshipsOfTodo).to.have.status(200);
    expect(categRelationshipsOfTodo.body).to.deep.equal(expected);
  });

  it("DELETE /todos/:id/categories/:id - Delete non-existing relationship instance between todo and category (eg after it has already been deleted)- Error Case", async function () {
    const todoID = 1;
    const categID = 1;
    const response = await chai
      .request(host)
      .delete(`${todosEndpoint}/${todoID}/${categRelationship}/${categID}`)
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);

    const secondAttemptResponse = await chai
      .request(host)
      .delete(`${todosEndpoint}/${todoID}/${categRelationship}/${categID}`)
      .set("Content-Type", "application/xml");
    const expected = {
      errorMessages: [
        `Could not find any instances with todos/${todoID}/categories/${categID}`,
      ],
    };
    expect(secondAttemptResponse.body).to.deep.equal(expected);
    expect(secondAttemptResponse).to.have.status(404);
  });
});
