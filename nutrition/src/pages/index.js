import React from "react"
import { Link } from "gatsby"

import Layout from "../components/layout"
import Image from "../components/image"
import SEO from "../components/seo"

const IndexPage = () => (
  <Layout>
    <SEO title="Home" />
    <h1 style={{ textAlign: `center` }}>Hi Lisa!</h1>
    <p style={{ textAlign: `center` }}>You're doing great today!</p>
    <div HealthScore style={{ 
      width: `1fr`, 
      height: `200px`, 
      backgroundColor: `#BC9CFF`, 
      marginBottom: `1.45rem`,
      borderRadius: `5`,
      }}>
      <h3 style={{
        marginTop: `20px`,
        color: `white`,
        textAlign: `center`
      }}>Today's score</h3>
    </div>
    <Link to="/page-2/">Go to page 2</Link>
  </Layout>
)

export default IndexPage
