const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const testConstants = require("../../testConstants.js");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");

const host = testConstants.host;
const categoriesEndpoint = testConstants.categsEndpoint;
const categProjRelationship = testConstants.categProjRelationship;
const validID = 1;
const validID2 = 2;
const invalidID = 20;

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/categories/:id/projects endpoint API Calls - XML", function () {
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
        .post(`${categoriesEndpoint}/${validID}/${categProjRelationship}`)
        .send({
          id: "1",
        });
    } catch (err) {}
  });

  afterEach(async function () {
    try {
      await chai.request(host).get("/shutdown");
    } catch (err) {}
  });

  it("HEAD /categories/:id/projects - Return headers for the project items related to category, with existing given id - Capability", async function () {
    const response = await chai
      .request(host)
      .head(`${categoriesEndpoint}/${validID}/${categProjRelationship}`)
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);
  });

  it("HEAD /categories/:id/projects - Return headers for the project items related to non existent category,- BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 200
    const response = await chai
      .request(host)
      .head(`${categoriesEndpoint}/${invalidID}/${categProjRelationship}`)
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);
  });

  it("POST /Categories/:id/projects - create an instance of a relationship named projects between category instance :id and the project instance represented by the id in the body of the message  - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN STATUS 201 AND CREATE CATEGORY-PROJECT RELATIONSHIP
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 400 AND RETURNS ERROR MESSAGE BECAUSE IT DOESNT ACCEPT THE XML INPUT
    const body = `<id>1</id>`;
    const response = await chai
      .request(host)
      .post(`${categoriesEndpoint}/${validID2}/${categProjRelationship}`)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected =
      '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}';
    expect(response).to.have.status(400);
    expect(response.text).to.deep.equal(expected);
  });

  it("POST /Categories/:id/projects - create an instance of a relationship named projects between category and project with nonexistent category ID  - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN STATUS 404
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 400 AND RETURNS ERROR MESSAGE BECAUSE IT DOESNT ACCEPT THE XML INPUT
    const body = `<id>1</id>`;
    const response = await chai
      .request(host)
      .post(`${categoriesEndpoint}/${invalidID}/${categProjRelationship}`)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected =
      '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}';
    expect(response).to.have.status(400);
    expect(response.text).to.deep.equal(expected);
  });

  it("POST /Categories/:id/projects - create an instance of a relationship named projects between category and project with nonexistent project ID in body  - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN STATUS 404
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 400 AND RETURNS ERROR MESSAGE BECAUSE IT DOESNT ACCEPT THE XML INPUT
    const body = `<id>20</id>`;
    const response = await chai
      .request(host)
      .post(`${categoriesEndpoint}/${validID}/${categProjRelationship}`)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected =
      '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}';
    expect(response).to.have.status(400);
    expect(response.text).to.deep.equal(expected);
  });

  it("DELETE /categories/:id/projects/:id - Delete existing relationship instance between category and project - Capability", async function () {
    const projID = 1;
    const response = await chai
      .request(host)
      .delete(
        `${categoriesEndpoint}/${validID}/${categProjRelationship}/${projID}`
      )
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);
    // Veryfying deletion through get request
    const relationship = await chai
      .request(host)
      .get(`${categoriesEndpoint}/${validID}/${categProjRelationship}`);
    const expected = {
      projects: [],
    };
    expect(relationship).to.have.status(200);
    expect(relationship.body).to.deep.equal(expected);
  });

  it("DELETE /categories/:id/todos/:id - Delete non-existing relationship instance between category and project- Error Case", async function () {
    const projID = 2;
    const response = await chai
      .request(host)
      .delete(
        `${categoriesEndpoint}/${validID}/${categProjRelationship}/${projID}`
      )
      .set("Content-Type", "application/xml");

    const expected = {
      errorMessages: [
        `Could not find any instances with categories/${validID}/projects/${projID}`,
      ],
    };
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equal(expected);
  });
});
