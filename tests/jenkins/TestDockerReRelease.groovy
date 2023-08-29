/*
 * Copyright OpenSearch Contributors
 * SPDX-License-Identifier: Apache-2.0
 */


import jenkins.tests.BuildPipelineTest
import org.junit.Before
import org.junit.Test
import static com.lesfurets.jenkins.unit.global.lib.LibraryConfiguration.library
import static com.lesfurets.jenkins.unit.global.lib.GitSource.gitSource
import static com.lesfurets.jenkins.unit.global.lib.LibraryConfiguration.library
import static com.lesfurets.jenkins.unit.global.lib.GitSource.gitSource

class TestDockerReRelease extends BuildPipelineTest {

    @Override
    @Before
    void setUp() {

        helper.registerSharedLibrary(
            library().name('jenkins')
                .defaultVersion('5.6.0')
                .allowOverride(true)
                .implicit(true)
                .targetPath('vars')
                .retriever(gitSource('https://github.com/opensearch-project/opensearch-build-libraries.git'))
                .build()
            )

        super.setUp()


        // Variables
        binding.setVariable('PRODUCT', 'opensearch')
        binding.setVariable('TAG', '1')
        binding.setVariable('RE_RELEASE', 'true')

    }

    @Test
    void DockerScan_test() {
        super.testPipeline('jenkins/docker/docker-re-release.jenkinsfile',
                'tests/jenkins/jenkinsjob-regression-files/docker/docker-re-release.jenkinsfile')
    }
}
