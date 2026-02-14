const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");
const testConstants = require("../../testConstants.js");

const host = testConstants.host;
const projectsEndpoint = testConstants.projectsEndpoint;
const categoriesEndpoint = testConstants.categsEndpoint;
const categoriesRelationship = testConstants.categoriesRelationship;
const validID = 1;
const invalidID = 20;

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/projects/:id/categories & /projects/:id/categories/:id endpoint API Calls - JSON", function () {
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

  it("GET /projects/:id/categories - Returns category items related to project w/ existing given id - Capability", async function () {
    const response = await chai
      .request(host)
      .get(`${projectsEndpoint}/${validID}/${categoriesRelationship}`);
    const expected = {
      categories: [
        {
          id: "1",
          title: "Office",
          description: "",
        },
      ],
    };

    expect(response).to.have.status(200);
    expect(response.body).to.deep.equal(expected);
  });

  it("GET /projects/:id/categories - Returns category items related to project w/ non-existing given id - BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404 AND ERROR MESSAGE SINCE PROJECT DOES NOT EXIST
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 200 AND LIST INCLUDING CATEGORY WHICH SHOULDNT BE THERE
    const response = await chai
      .request(host)
      .get(`${projectsEndpoint}/${invalidID}/${categoriesRelationship}`);
    //EXPECTED an error message but this is a bug
    const expected = {
      categories: [
        {
          id: "1",
          title: "Office",
          description: "",
        },
      ],
    };

    expect(response).to.have.status(200);
    expect(response.body).to.deep.equal(expected);
  });

  it("HEAD /projects/:id/categories - Return headers for the category items related to project, with existing given id - Capability", async function () {
    const response = await chai
      .request(host)
      .head(`${projectsEndpoint}/${validID}/${categoriesRelationship}`);
    expect(response).to.have.status(200);
  });

  it("HEAD /projects/:id/categories - Return headers for the category items related to non-existing project,- BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 200
    const response = await chai
      .request(host)
      .head(`${projectsEndpoint}/${invalidID}/${categoriesRelationship}`);
    //Actual Expected status is 404
    expect(response).to.have.status(200);
  });

  it("POST /projects/:id/categories - Create relationship between specified existing project and existing category instance - Capability", async function () {
    const body = {
      id: "2",
    };
    const response = await chai
      .request(host)
      .post(`${projectsEndpoint}/${validID}/${categoriesRelationship}`)
      .send(body);
    expect(response).to.have.status(201);

    //Verifying that the relationship persists
    const relationship = await chai
      .request(host)
      .get(`${projectsEndpoint}/${validID}/${categoriesRelationship}`);
    const expected = {
      categories: [
        {
          id: "1",
          title: "Office",
          description: "",
        },
        {
          id: "2",
          title: "Home",
          description: "",
        },
      ],
    };
    expect(relationship).to.have.status(200);
    expect(relationship.body).to.deep.equalInAnyOrder(expected);
  });

  it("POST /projects/:id/categories - Create relationship between specified non-existing project and existing category instance - Error Case", async function () {
    const body = {
      id: "1",
    };
    const expected = {
      errorMessages: [
        `Could not find parent thing for relationship projects/${invalidID}/categories`,
      ],
    };
    const response = await chai
      .request(host)
      .post(`${projectsEndpoint}/${invalidID}/${categoriesRelationship}`)
      .send(body);
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equal(expected);
  });

  it("DELETE /projects/:id/categories/:id - Delete existing relationship instance between project and category - Capability", async function () {
    const categID = 1;
    const response = await chai
      .request(host)
      .delete(
        `${projectsEndpoint}/${validID}/${categoriesRelationship}/${categID}`
      );
    expect(response).to.have.status(200);

    // Veryfying deletion through get request
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
      );

    const expected = {
      errorMessages: [
        `Could not find any instances with projects/${validID}/categories/${categID}`,
      ],
    };
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equal(expected);
  });

  it("POST /projects/:id/categories - Create relationship between specified non-existing project and existing category instance - BUG", async function () {
    // EXPECTED BEHAVIOR: EXISTENT RELATIONSHIP ON BOTH PROJECT AND CATEGORY SIDE FOR BIDIRECTIONALITY TO BE SATISFIED
    // ACTUAL BEHAVIOR: UNIDIRECTIONAL RELATIONSHIP ON PROJECT SIDE ONLY

    const body = {
      id: "2",
    };

    const response = await chai
      .request(host)
      .post(`${projectsEndpoint}/${validID}/${categoriesRelationship}`)
      .send(body);
    expect(response).to.have.status(201);

    //Checking that the relationship exists from projects=>category (SUCCESS - EXISTENT)
    const relationship = await chai
      .request(host)
      .get(`${projectsEndpoint}/${validID}/${categoriesRelationship}`);
    const expected = {
      categories: [
        {
          id: "1",
          title: "Office",
          description: "",
        },
        {
          id: "2",
          title: "Home",
          description: "",
        },
      ],
    };
    expect(relationship).to.have.status(200);
    expect(relationship.body).to.deep.equalInAnyOrder(expected);

    //Checking if category=>projects relationship is created (bidirectionality) (BUG - NON-EXISTENT)
    const categProjectRel = await chai
      .request(host)
      .get(`${categoriesEndpoint}/${body.id}/${projectsEndpoint}`);
    const expectedRel = {
      projects: [],
    };
    expect(categProjectRel).to.have.status(200);
    expect(categProjectRel.body).to.deep.equal(expectedRel);
  });
});
