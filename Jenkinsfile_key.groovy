#!groovy
//variables from jenkins
properties([disableConcurrentBuilds()])
agent = env.agent // work agent
token = env.token // openstack token
stand = env.stand // openstack stand
hosts_limit = env.hosts_limit // hosts limit
keys_repo_url = env.keys_repo_url // url for keys repo
keys_repo_cred = env.keys_repo_cred // key repository credantials
user_limit = env.user_limit // user
user_type = env.user_type // choice method

list_of_variables = [agent: agent,
                     token : token,
                     stand: stand,
                     hosts_limit: hosts_limit,
                     keys_repo_url: keys_repo_url,
                     keys_repo_cred: keys_repo_cred,
                     user_limit: user_limit,
                     user_type: user_type]

pipeline {
    agent {
        label agent
        }
    options {
        buildDiscarder(logRotator(numToKeepStr: '1', artifactNumToKeepStr: '1'))
    }
    stages {
        stage('Run dynamic inventory script') {
            steps {
                script {
                    stage('whoami') {
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
                }
            }
        }
        stage('scp pub keys repository') {
            steps {
                dir('keys') {
                    git branch: 'master',
                        credentialsId: keys_repo_cred,
                        url: keys_repo_url
                }
            }
        }
        stage("prepare keys") {
            steps {
                script {
                    if (user_limit == null) {
                        sh 'ls keys'
                    }
                    else {
//                         sh 'ls | grep -v "${user_limit}" | xargs rm'
//                         sh 'rm $(find key_test -name test3 -type f)'
                        sh 'ls keys | grep -v $(find keys -name ${user_limit} -type f -printf "%f\n")'
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
                                playbook: 'playbook_key.yaml',
                                inventory: 'inventory.yml',
                                tags: user_type,
                                colorized: true)
                        }
                    }
                    else {
                        ansiColor('xterm'){
                            ansiblePlaybook(
                                playbook: 'playbook_key.yaml',
                                inventory: 'inventory.yml',
                                tags: user_type,
                                limit: hosts_limit,
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
        }
    }
}