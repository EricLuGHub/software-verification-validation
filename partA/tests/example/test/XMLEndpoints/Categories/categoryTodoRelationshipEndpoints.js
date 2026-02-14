const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const testConstants = require("../../testConstants.js");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");

const host = testConstants.host;
const categoriesEndpoint = testConstants.categsEndpoint;
const categTodosRelationship = testConstants.categTodosRelationship;
const validID = 1;
const invalidID = 20;

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/categories/:id/todos and /categories/:id/todos/:id endpoint API Calls - XML", function () {
  beforeEach(async function () {
    child_process.spawn("java", ["-jar", "runTodoManagerRestAPI-1.5.5.jar"]);
    let serverReady = false;
    while (!serverReady) {
      try {
        await chai.request(host).get(categoriesEndpoint);
        serverReady = true;
      } catch (err) {}
    }
  });

  beforeEach(async () => {
    try {
      await chai
        .request(host)
        .post(`${categoriesEndpoint}/${validID}/${categTodosRelationship}`)
        .send({
          id: "2",
        });
    } catch (err) {}
  });

  afterEach(async function () {
    try {
      await chai.request(host).get("/shutdown");
    } catch (err) {}
  });

  it("HEAD /categories/:id/todos - Return headers for the todo items related to category, with existing given id - Capability", async function () {
    const response = await chai
      .request(host)
      .head(`${categoriesEndpoint}/${validID}/${categTodosRelationship}`)
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);
  });

  it("HEAD /categories/:id/todos - Return headers for the todo items related to non-existing category,- BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 200
    const response = await chai
      .request(host)
      .head(`${categoriesEndpoint}/${invalidID}/${categTodosRelationship}`)
      .set("Content-Type", "application/xml");
    //Actual Expected status is 404
    expect(response).to.have.status(200);
  });

  it("POST /categories/:id/todos - Create relationship between specified existing category and existing todo instance - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN STATUS 404
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 400 AND RETURNS ERROR MESSAGE BECAUSE IT DOESNT ACCEPT THE XML INPUT
    const body = `<id>1</id>`;
    const response = await chai
      .request(host)
      .post(`${categoriesEndpoint}/${validID}/${categTodosRelationship}`)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected =
      '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}';
    expect(response).to.have.status(400);
    expect(response.text).to.deep.equal(expected);
  });

  it("POST /categories/:id/todos - Create relationship between specified nonexistent category and existing todo instance - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN STATUS 404
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 400 AND RETURNS ERROR MESSAGE BECAUSE IT DOESNT ACCEPT THE XML INPUT
    const body = `<id>1</id>`;
    const response = await chai
      .request(host)
      .post(`${categoriesEndpoint}/${invalidID}/${categTodosRelationship}`)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected =
      '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}';
    expect(response).to.have.status(400);
    expect(response.text).to.deep.equal(expected);
  });

  it("DELETE /categories/:id/todos - Delete existing relationship instance between category and todo - Capability", async function () {
    const todoID = 2;
    const response = await chai
      .request(host)
      .delete(
        `${categoriesEndpoint}/${validID}/${categTodosRelationship}/${todoID}`
      )
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);

    // Verifying deletion through get request
    const relationship = await chai
      .request(host)
      .get(`${categoriesEndpoint}/${validID}/${categTodosRelationship}`)
      .set("Content-Type", "application/xml");
    const expected = {
      todos: [],
    };

    expect(relationship).to.have.status(200);
    expect(relationship.body).to.deep.equal(expected);
  });

  it("DELETE /categories/:id/todos/:id - Delete non-existing relationship instance between category and todo- Error Case", async function () {
    const todoID = 20;
    const response = await chai
      .request(host)
      .delete(
        `${categoriesEndpoint}/${validID}/${categTodosRelationship}/${todoID}`
      )
      .set("Content-Type", "application/xml");

    const expected = {
      errorMessages: [
        `Could not find any instances with categories/${validID}/todos/${todoID}`,
      ],
    };
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equal(expected);
  });
});
