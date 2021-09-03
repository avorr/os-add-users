#!groovy
//variables from jenkins
properties([disableConcurrentBuilds()])
agent = env.agent // work agent
token = env.token // openstack token
stand = env.stand // openstack stand
hosts_limit = env.hosts_limit // hosts limit
credentials = env.credentials // cred for users
user_type = env.user_type // user type: sudo or without sudo

list_of_variables = [agent: agent,
                     token : token,
                     stand: stand,
                     hosts_limit: hosts_limit,
                     credentials: credentials,
                     user_type: user_type]

pipeline {
    agent {
        label agent
        }
    options {
        buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '10'))
    }

    stages {
        stage('creating dynamic inventory') {
            steps {
                script {
                    stage('WHOAMI') {
                        wrap([$class: 'BuildUser']) {
                            def user = env.BUILD_USER_ID
                        println(env.WORKSPACE)
                        println(env.BUILD_USER)
                        }
                    }
                    wrap([$class: 'MaskPasswordsBuildWrapper', varPasswordPairs: [[password: token, var: 'PSWD']]]) {
                        stage('run script dynamic_inventory') {
                            catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                                sh 'python3 dynamic_inventory.py ${token} ${stand}'
                            }
                        }
                    }
                    wrap([$class: 'MaskPasswordsBuildWrapper', varPasswordPairs: [[password: credentials, var: 'PSWD']]]) {
                        stage('run script dynamic vars') {
                            catchError(buildResult: 'SUCCESS', stageResult: 'FAILURE') {
                                sh 'python3 create_vars.py ${credentials}'
                            }
                        }
                    }
                }
            }
        }
        stage("run ansible-playbook") {
            steps {
                script {
                    if (hosts_limit == null) {
                        ansiColor('xterm'){
                            ansiblePlaybook(
                                playbook: 'playbook.yaml',
                                inventory: 'inventory.yml',
                                tags: user_type,
                                colorized: true)
                        }
                    }


                    else {
                        ansiColor('xterm'){
                            ansiblePlaybook(
                                playbook: 'playbook.yaml',
                                inventory: 'inventory.yml',
                                limit: hosts_limit,
                                tags: user_type,
                                colorized: true)
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            sh 'truncate -s0 inventory.yml'
            sh 'truncate -s0 vars.yml'
        }
    }
}
