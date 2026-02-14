const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");
const testConstants = require("../../testConstants.js");

const host = testConstants.host;
const projectsEndpoint = testConstants.projectsEndpoint;
const categoriesRelationship = testConstants.categoriesRelationship;
const validID = 1;
const invalidID = 20;

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/projects/:id/categories & /projects/:id/categories/:id endpoint API Calls - XML", function () {
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

  //Setting up a relationship between project and category for tests
  beforeEach(async () => {
    try {
      await chai
        .request(host)
        .post(`${projectsEndpoint}/${validID}/${categoriesRelationship}`)
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

  it("HEAD /projects/:id/categories - Return headers for the category items related to project, with existing given id - Capability", async function () {
    const response = await chai
      .request(host)
      .head(`${projectsEndpoint}/${validID}/${categoriesRelationship}`)
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);
  });

  it("HEAD /projects/:id/categories - Return headers for the category items related to non-existing project,- BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 200
    const response = await chai
      .request(host)
      .head(`${projectsEndpoint}/${invalidID}/${categoriesRelationship}`)
      .set("Content-Type", "application/xml");
    //Actual Expected status is 404
    expect(response).to.have.status(200);
  });

  it("POST /projects/:id/categories - Create relationship between specified existing project and existing category instance - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN STATUS CODE 201 AND CREATE RELATIONSHIP ENTITY BIDIRECTIONALLY
    // ACTUAL BEHAVIOR: RETURN ERROR CODE 404 AND ERROR TEXT MESSAGE DUE TO INABILITY TO READ XML
    const body = `<id>2</id>`;
    const response = await chai
      .request(host)
      .post(`${projectsEndpoint}/${validID}/${categoriesRelationship}`)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected =
      '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}';
    expect(response).to.have.status(400);
    expect(response.text).to.deep.equal(expected);
  });

  it("POST /projects/:id/categories - Create relationship between specified non-existing project and existing category instance - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404 AND ERROR MESSAGE: "Could not find parent thing for relationship project/20/categories"
    // ACTUAL BEHAVIOR: RETURN ERROR CODE 400 AND ERROR MESSAGE DUE TO INABILITY TO READ XML
    const body = `<id>2</id>`;
    const response = await chai
      .request(host)
      .post(`${projectsEndpoint}/${invalidID}/${categoriesRelationship}`)
      .set("Content-Type", "application/xml")
      .send(body);
    const expected =
      '{"errorMessages":["java.lang.IllegalStateException: Expected BEGIN_OBJECT but was STRING at line 1 column 1 path $"]}';
    expect(response).to.have.status(400);
    expect(response.text).to.deep.equal(expected);
  });

  it("DELETE /projects/:id/categories/:id - Delete existing relationship instance between project and category - Capability", async function () {
    const categID = 1;
    const response = await chai
      .request(host)
      .delete(
        `${projectsEndpoint}/${validID}/${categoriesRelationship}/${categID}`
      )
      .set("Content-Type", "application/xml");
    expect(response).to.have.status(200);

    // Verifying deletion through get request
    const relationship = await chai
      .request(host)
      .get(`${projectsEndpoint}/${validID}/${categoriesRelationship}`);
    const expected = {
      categories: [],
    };

    expect(relationship).to.have.status(200);
    expect(relationship.body).to.deep.equal(expected);
  });

  it("DELETE /todos/:id/categories/:id - Delete non-existing relationship instance between project and category- Error Case", async function () {
    const categID = 2;
    const response = await chai
      .request(host)
      .delete(
        `${projectsEndpoint}/${validID}/${categoriesRelationship}/${categID}`
      )
      .set("Content-Type", "application/xml");

    const expected = {
      errorMessages: [
        "Could not find any instances with projects/1/categories/2",
      ],
    };
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equal(expected);
  });
});
