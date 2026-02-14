const expect = require("chai").expect;
const child_process = require("child_process");
const chai = require("chai");
const chaiHttp = require("chai-http");
const testConstants = require("../../testConstants.js");
const deepEqualInAnyOrder = require("deep-equal-in-any-order");

const host = testConstants.host;
const categoriesEndpoint = testConstants.categsEndpoint;
const categProjRelationship = testConstants.categProjRelationship;
const projectsEndpoint = testConstants.projectsEndpoint;
const categoriesRelationship = testConstants.categoriesRelationship;
const validID = 1;
const validID2 = 2;
const invalidID = 20;

chai.use(chaiHttp);
chai.use(deepEqualInAnyOrder);

describe("/Categories/:id/projects endpoint API Calls - JSON", function () {
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

  it("GET /Categories/:id/projects - return all the project items related to category with existing category ID  - Capability", async function () {
    const response = await chai
      .request(host)
      .get(`${categoriesEndpoint}/${validID}/${categProjRelationship}`);
    const expected = {
      projects: [
        {
          id: "1",
          title: "Office Work",
          completed: "false",
          active: "false",
          description: "",
          tasks: [
            {
              id: "2",
            },
            {
              id: "1",
            },
          ],
        },
      ],
    };

    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("GET /Categories/:id/projects - return all the project items related to category with a nonexistent category ID  - Bug", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404 AND ERROR MESSAGE SINCE CATEGORY DOES NOT EXIST
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 200 AND LIST INCLUDING PROJECT WHICH SHOULDNT BE THERE
    const response = await chai
      .request(host)
      .get(`${categoriesEndpoint}/${invalidID}/${categProjRelationship}`);
    const expected = {
      projects: [
        {
          id: "1",
          title: "Office Work",
          completed: "false",
          active: "false",
          description: "",
          tasks: [
            {
              id: "2",
            },
            {
              id: "1",
            },
          ],
        },
      ],
    };

    expect(response).to.have.status(200);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("HEAD /categories/:id/projects - Return headers for the project items related to category, with existing given id - Capability", async function () {
    const response = await chai
      .request(host)
      .head(`${categoriesEndpoint}/${validID}/${categProjRelationship}`);
    expect(response).to.have.status(200);
  });

  it("HEAD /categories/:id/projects - Return headers for the project items related to non existent category,- BUG", async function () {
    // EXPECTED BEHAVIOR: RETURN ERROR CODE 404
    // ACTUAL BEHAVIOR: RETURN STATUS CODE 200
    const response = await chai
      .request(host)
      .head(`${categoriesEndpoint}/${invalidID}/${categProjRelationship}`);
    expect(response).to.have.status(200);
  });

  it("POST /Categories/:id/projects - create an instance of a relationship named projects between category instance :id and the project instance represented by the id in the body of the message  - Capability", async function () {
    const body = {
      id: "1",
    };
    const response = await chai
      .request(host)
      .post(`${categoriesEndpoint}/${validID2}/${categProjRelationship}`)
      .send(body);
    expect(response).to.have.status(201);
  });

  it("POST /Categories/:id/projects - create an instance of a relationship named projects between category and project with nonexistent category ID  - Error Case", async function () {
    const body = {
      id: "1",
    };
    const expected = {
      errorMessages: [
        "Could not find parent thing for relationship categories/20/projects",
      ],
    };
    const response = await chai
      .request(host)
      .post(`${categoriesEndpoint}/${invalidID}/${categProjRelationship}`)
      .send(body);
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("POST /Categories/:id/projects - create an instance of a relationship named projects between category and project with nonexistent project ID in body  - Error Case", async function () {
    const body = {
      id: "20",
    };
    const expected = {
      errorMessages: ["Could not find thing matching value for id"],
    };
    const response = await chai
      .request(host)
      .post(`${categoriesEndpoint}/${validID}/${categProjRelationship}`)
      .send(body);
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equalInAnyOrder(expected);
  });

  it("DELETE /categories/:id/projects/:id - Delete existing relationship instance between category and project - Capability", async function () {
    const projID = 1;
    const response = await chai
      .request(host)
      .delete(
        `${categoriesEndpoint}/${validID}/${categProjRelationship}/${projID}`
      );
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

  it("DELETE /categories/:id/projects/:id - delete relationship between specified category and nonexistent project instance - Error Case", async function () {
    const projID = 2;
    const response = await chai
      .request(host)
      .delete(
        `${categoriesEndpoint}/${validID}/${categProjRelationship}/${projID}`
      );

    const expected = {
      errorMessages: [
        `Could not find any instances with categories/${validID}/projects/${projID}`,
      ],
    };
    expect(response).to.have.status(404);
    expect(response.body).to.deep.equal(expected);
  });

  it("POST /Categories/:id/projects - create an instance of a relationship named projects between category instance :id and the project instance represented by the id in the body of the message  - BUG", async function () {
    // EXPECTED BEHAVIOR: BIDIRECTIONALITY FOR CATEGORY <=> PROJECT EXISTS
    // ACTUAL BEHAVIOR: ONLY THE CATEGORY => PROJECT RELATIONSHIP EXISTS
    const body = {
      id: "1",
    };
    const response = await chai
      .request(host)
      .post(`${categoriesEndpoint}/${validID2}/${categProjRelationship}`)
      .send(body);
    expect(response).to.have.status(201);

    //Checking that the relationship exists from category=>projects
    const relationship = await chai
      .request(host)
      .get(`${categoriesEndpoint}/${validID2}/${categProjRelationship}`);
    const expected = {
      projects: [
        {
          id: "1",
          title: "Office Work",
          completed: "false",
          active: "false",
          description: "",
          tasks: [
            {
              id: "1",
            },
            {
              id: "2",
            },
          ],
        },
      ],
    };
    expect(relationship).to.have.status(200);
    expect(relationship.body).to.deep.equalInAnyOrder(expected);

    //Checking if project=>category relationship is created (FAILURE - NONEXISTENT)
    const projCategoryRel = await chai
      .request(host)
      .get(`${projectsEndpoint}/${body.id}/${categoriesRelationship}`);
    const expectedRel = {
      categories: [],
    };
    expect(projCategoryRel).to.have.status(200);
    expect(projCategoryRel.body).to.deep.equalInAnyOrder(expectedRel);
  });

  it("DELETE /categories/:id/projects/:id - Delete existing relationship instance between category and project - Capability", async function () {
    const projID = 1;
    const response = await chai
      .request(host)
      .delete(
        `${categoriesEndpoint}/${validID}/${categProjRelationship}/${projID}`
      );
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

    //Checking if projects=>categories relationship is deleted (SUCCESS)
    const projCategoryRel = await chai
      .request(host)
      .get(`${projectsEndpoint}/${projID}/${categoriesRelationship}`);
    const expectedProj = {
      categories: [],
    };
    expect(projCategoryRel).to.have.status(200);
    expect(projCategoryRel.body).to.deep.equalInAnyOrder(expectedProj);
  });
});
